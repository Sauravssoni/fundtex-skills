"""FundTex India Intraday Research Desk: causal ORB and non-executable session replay.

Original engineering inspiration: Jake Schincariol, day-trader-skill (MIT, 2026)
https://github.com/Jakeschincariol/day-trader-skill
This implementation is original, India/IST-specific, offline-only and paper-only.
Market holidays / special sessions require a verified official calendar; no
network/broker/account/order calls or claimed executable fills.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from zoneinfo import ZoneInfo
import csv, json, math, random, statistics
from .market import validate_symbol

IST=ZoneInfo("Asia/Kolkata")
OPEN=time(9,15)
CLOSE=time(15,30)
BARS=75
MAX_BYTES=9_000_000
FIELDS=("timestamp","symbol","open","high","low","close","volume")
def _number(v,field,positive=True):
    if isinstance(v,bool):raise ValueError("Invalid "+field)
    try:n=float(v)
    except (TypeError,ValueError):raise ValueError("Invalid "+field) from None
    if not math.isfinite(n) or (n<=0 if positive else n<0):
        raise ValueError("Invalid "+field)
    return n
def _bar(raw,expected_symbol):
    if raw["symbol"].strip().upper()!=expected_symbol:
        raise ValueError("Mixed symbols in intraday feed")
    stamp=raw["timestamp"].strip()
    try:t=datetime.fromisoformat(stamp.replace("Z","+00:00"))
    except ValueError:raise ValueError("Timestamp not ISO8601") from None
    if t.tzinfo is None:
        raise ValueError("Intraday timestamp requires exchange timezone offset")
    if t.utcoffset() is None:raise ValueError("Invalid timezone")
    local=t.astimezone(IST)
    if local.utcoffset()!=timedelta(hours=5,minutes=30):
        raise ValueError("Exchange timezone mismatch")
    minute=local.hour*60+local.minute
    start=9*60+15
    if not start<=minute<15*60+30 or (minute-start)%5!=0 or local.second or local.microsecond:
        raise ValueError("Only exchange-grid 5m candle START times supported")
    o,h,l,c=[_number(raw[k],k) for k in ("open","high","low","close")]
    v=_number(raw["volume"],"volume",positive=False)
    if not (l<=min(o,c)<=max(o,c)<=h):
        raise ValueError("Impossible OHLC candle")
    return {"timestamp":local.isoformat(),"date":local.date().isoformat(),
            "slot":(minute-start)//5,"open":o,"high":h,"low":l,"close":c,"volume":v}
def load_sessions(path,symbol,*,require_full=True):
    sym=validate_symbol(symbol)
    file=Path(path).expanduser()
    if not file.is_file() or file.is_symlink() or not 0<file.stat().st_size<=MAX_BYTES:
        raise ValueError("Approved bounded 5m OHLCV CSV required")
    with file.open("r",newline="",encoding="utf-8-sig") as fh:
        r=csv.DictReader(fh)
        if not r.fieldnames or not set(FIELDS).issubset(set(r.fieldnames)):
            raise ValueError("Require timestamp,symbol,open,high,low,close,volume columns")
        arr=[_bar(x,sym) for x in r]
    if len(arr)<20*BARS or len(arr)>100*BARS:
        raise ValueError("At least 20 complete historical trading sessions, max 100")
    if [x["timestamp"] for x in arr]!=sorted(x["timestamp"] for x in arr):
        raise ValueError("Unsorted timestamps")
    groups=defaultdict(list)
    for x in arr:groups[x["date"]].append(x)
    # Refuse half sessions, duplicate slots, missing bars, special trading
    # sessions and current incomplete day rather than fabricate bar history.
    if require_full:
        for d,bars in groups.items():
            if len(bars)!=BARS or [b["slot"] for b in bars]!=list(range(BARS)):
                raise ValueError("Incomplete/duplicate/nonstandard session "+d)
            if date.fromisoformat(d).weekday()>=5:
                raise ValueError("Weekend/special session needs verified calendar "+d)
    today=datetime.now(IST).date()
    if any(date.fromisoformat(d)>today for d in groups):
        raise ValueError("Future observations not permitted")
    # Date labels alone do not certify NSE operating day or data source.
    return {"symbol":sym,"sessions":dict(groups),
            "source_sha256":sha256(file.read_bytes()).hexdigest(),
            "data_quality":"USER_SUPPLIED_NOT_EXCHANGE_VERIFIED",
            "official_holiday_calendar_verified":False,
            "completed_session_grid_verified":True,
            "broker_connected":False}

def opening_range(session,*,or_bars=3,until_slot=BARS):
    if isinstance(or_bars,bool) or not isinstance(or_bars,int) or not 1<=or_bars<=6:
        raise ValueError("Opening range must be 1..6 complete 5m bars")
    if not or_bars<until_slot<=BARS:raise ValueError("Invalid as-of grid")
    complete=session[:until_slot]
    if len(complete)<until_slot or [x["slot"] for x in complete]!=list(range(until_slot)):
        raise ValueError("Incomplete candle history")
    high=max(x["high"] for x in complete[:or_bars])
    low=min(x["low"] for x in complete[:or_bars])
    # Trigger only after CLOSE of a bar beyond opening range; no entry on a wick.
    trigger=next((x for x in complete[or_bars:] if x["close"]>high),None)
    return {"status":"TRIGGERED" if trigger else "WAITING",
            "opening_high":high,"opening_low":low,
            "first_completed_trigger_slot":trigger["slot"] if trigger else None,
            "trigger_close":trigger["close"] if trigger else None,
            "trigger_candle_start_ist":trigger["timestamp"] if trigger else None,
            "entry_is_next_candle_open_not_trigger_close":True,
            "as_of_last_completed_bar":complete[-1]["timestamp"]}
def _plan(*,entry,stop,target,quantity,risk_budget,fees_per_side=0.0005,slippage_per_side=0.0005):
    entry,stop,target=[_number(x,k) for x,k in ((entry,"entry"),(stop,"stop"),(target,"target"))]
    qty=int(quantity)
    if isinstance(quantity,bool) or qty!=quantity or not 1<=qty<=100000:
        raise ValueError("Quantity must be integer shares 1..100000")
    risk_budget=_number(risk_budget,"risk_budget")
    if not 0<=fees_per_side<=.05 or not 0<=slippage_per_side<=.05:
        raise ValueError("Invalid explicit fee/slippage assumptions")
    if not stop<entry<target:raise ValueError("Long-only defined stop and target geometry required")
    friction=2*(fees_per_side+slippage_per_side)*entry*qty
    estimated_stop_loss=(entry-stop)*qty+friction
    # Not a guarantee: gap/slippage may exceed stop cost
    return {"entry":entry,"stop":stop,"target":target,"quantity":qty,
            "risk_budget_inr":risk_budget,"fees_per_side_rate_assumed":fees_per_side,
            "slippage_per_side_rate_assumed":slippage_per_side,
            "estimated_stop_loss_inr":round(estimated_stop_loss,2),
            "max_loss_is_not_guaranteed":True,"defined_loss_approximation_only":True,
            "risk_status":"PAPER_ELIGIBLE" if estimated_stop_loss<=risk_budget else "BLOCK_PAPER_RISK"}
def paper_plan(data,*,session_date,quantity=1,risk_budget=1000,or_bars=3,as_of_slot=BARS):
    if session_date not in data["sessions"]:raise ValueError("Session not in approved history")
    dates=list(data["sessions"])
    idx=dates.index(session_date)
    if idx<20:raise ValueError("20 prior full sessions required; never sample future sessions")
    bars=data["sessions"][session_date]
    signal=opening_range(bars,or_bars=or_bars,until_slot=as_of_slot)
    if signal["status"]!="TRIGGERED":
        return {"signal":signal,"state":"NO_TRADE","orders_enabled":False}
    slot=signal["first_completed_trigger_slot"]
    if slot+1>=as_of_slot:
        return {"signal":signal,"state":"NEXT_BAR_NOT_YET_CLOSED","orders_enabled":False}
    # Historical execution modelling at the NEXT bar's open avoids same-bar fill.
    entry=bars[slot+1]["open"]
    stop=signal["opening_low"]
    if entry<=stop:return {"signal":signal,"state":"INVALID_NEXT_OPEN","orders_enabled":False}
    target=entry+2*(entry-stop)
    plan=_plan(entry=entry,stop=stop,target=target,quantity=quantity,risk_budget=risk_budget)
    return {"signal":signal,"plan":plan,"state":plan["risk_status"],
            "historical_entry_slot":slot+1,
            "source_sha256":data["source_sha256"],"source_quality":data["data_quality"],
            "historical_date":session_date,"orders_enabled":False,"paper_only":True}

def _run_path(prices,plan,*,start_slot,stop_conservative=True):
    """Never imply actual order execution. Stop-before-target is pessimistic for same bar."""
    price=plan["entry"];stop=plan["stop"];target=plan["target"]
    end="close";exit_price=price
    for b in prices[start_slot:]:
        if b["open"]<=stop:
            end="gap_stop";exit_price=b["open"];break
        if b["open"]>=target:
            end="gap_target";exit_price=b["open"];break
        stop_hit=b["low"]<=stop
        target_hit=b["high"]>=target
        if stop_hit and target_hit:
            end="both_hit_stop_first";exit_price=stop;break
        if stop_hit:end="stop";exit_price=stop;break
        if target_hit:end="target";exit_price=target;break
        exit_price=b["close"]
    qty=plan["quantity"]
    fees=plan["fees_per_side_rate_assumed"]+plan["slippage_per_side_rate_assumed"]
    net=(exit_price-price)*qty-(exit_price+price)*qty*fees
    return {"exit_case":end,"exit_price":exit_price,"net_pnl_inr":net,"red":net<0}

def replay(data,plan_obj,*,paths=10000,seed=19,window=2):
    if plan_obj.get("state")!="PAPER_ELIGIBLE":raise ValueError("A permitted paper risk verdict is required")
    if any(isinstance(x,bool) or not isinstance(x,int) for x in (paths,seed,window)):
        raise ValueError("Simulation controls must be bounded integers")
    if not 100<=paths<=1000000 or not 0<=seed<=2**32-1 or not 0<=window<=3:
        raise ValueError("Bounded paths 100..1,000,000, seed and resampling window required")
    dates=list(data["sessions"])
    d=plan_obj["historical_date"]
    i=dates.index(d)
    if i<20:raise ValueError("20 prior sessions required")
    prior=[data["sessions"][x] for x in dates[:i]]
    # Exclude target date and all later sessions by construction.
    entry_slot=plan_obj["historical_entry_slot"]
    plan=plan_obj["plan"]
    rng=random.Random(seed)
    results=[];counts=defaultdict(int)
    for _ in range(paths):
        prev=plan["entry"]
        sample=[]
        for slot in range(entry_slot,BARS):
            pos=max(1,min(BARS-1,slot+rng.randint(-window,window)))
            hist=rng.choice(prior)
            past=hist[pos];base=hist[pos-1]["close"]
            if base<=0:raise ValueError("Unusable previous bar close")
            p={k:prev*past[k]/base for k in ("open","high","low","close")}
            # Rebased bars preserve geometry only if previous close is positive.
            sample.append(p);prev=p["close"]
        case=_run_path(sample,plan,start_slot=0)
        counts[case["exit_case"]]+=1
        results.append(case["net_pnl_inr"])
    sorted_results=sorted(results)
    def pct(q):return sorted_results[int((len(sorted_results)-1)*q)]
    # Net outcome distribution is conditional on historical bar regimes,
    # not actual forward odds, and cannot certify a stop's maximum loss.
    return {"engine":"FUNDTEX_INDIA_INTRADAY_PAPER_REPLAY_V1",
            "symbol":data["symbol"],"source_sha256":data["source_sha256"],
            "source_quality":data["data_quality"],"historical_date":d,
            "source_sessions_used":len(prior),"future_sessions_sampled":False,
            "entry_date_excluded_from_pool":True,"exit_cases":dict(counts),
            "paths":paths,"seed":seed,"window":window,
            "probability_positive_net":sum(x>0 for x in results)/paths,
            "probability_loss":sum(x<0 for x in results)/paths,
            "mean_net_pnl_inr":statistics.mean(results),
            "median_net_pnl_inr":pct(.5),"p05_net_pnl_inr":pct(.05),
            "p95_net_pnl_inr":pct(.95),
            "worst_simulated_net_pnl_inr":sorted_results[0],
            "pessimistic_intrabar_stop_first":True,
            "market_holidays_exchange_verified":False,
            "model_quality":"RESAMPLED_HISTORICAL_BARS_NOT_PROBABILISTIC_FORECAST",
            "real_orders":0,"broker_order_permissions_required":False,
            "real_time_market_data_verified":False,
            "release_gate":"RESEARCH_ONLY_NOT_LIVE_TRADE_VALIDATED",
            "limitations":["Market holidays, auction gaps and corporate actions may break assumptions",
             "Stop price is never guaranteed and real losses may exceed simulation",
             "Fee/slippage assumptions are illustrative, not a current verified Indian fee schedule",
             "Forward test, liquidity, latency, survivorship and data licensing not verified",
             "Past bar resampling cannot represent every future path or news-driven jump"]}

def run_csv(csv_file,symbol,*,session_date,quantity=1,risk_budget=1000,
            as_of_slot=BARS,or_bars=3,paths=10000,seed=19):
    data=load_sessions(csv_file,symbol)
    plan=paper_plan(data,session_date=session_date,quantity=quantity,
                    risk_budget=risk_budget,as_of_slot=as_of_slot,or_bars=or_bars)
    return {"plan":plan,"replay":replay(data,plan,paths=paths,seed=seed)
            if plan["state"]=="PAPER_ELIGIBLE" else None,
            "orders_enabled":False,"real_trades":0}
