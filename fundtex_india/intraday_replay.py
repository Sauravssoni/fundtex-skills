"""India-specific intraday ORB replay, paper-only, with full-session quality gates.

Method adapted independently from general opening-range/time-machine concepts;
no code copied from Jake Schincariol's MIT skills. No exchange API or broker calls.
"""
from __future__ import annotations
import csv
from collections import defaultdict
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import hashlib
import math
import random
import statistics

IST=ZoneInfo("Asia/Kolkata")
def _read_bars(path,symbol):
    from .market import validate_symbol
    symbol=validate_symbol(symbol)
    f=Path(path).expanduser()
    if not f.is_file() or f.is_symlink() or f.stat().st_size>5_000_000:
        raise ValueError("Approved bounded observed intraday CSV required")
    sessions=defaultdict(list)
    with f.open("r",newline="",encoding="utf-8-sig") as stream:
        reader=csv.DictReader(stream)
        required={"timestamp","symbol","open","high","low","close","volume"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Observed 5m CSV must include timestamp,symbol,open,high,low,close,volume")
        for item in reader:
            if (item.get("symbol") or "").strip().upper()!=symbol:
                raise ValueError("Intraday file mixes instruments; reject to prevent ticker confusion")
            try:dt=datetime.fromisoformat(item["timestamp"].replace("Z","+00:00"))
            except (ValueError,TypeError):raise ValueError("Invalid exchange timestamp") from None
            if dt.tzinfo is None:raise ValueError("Intraday timestamp MUST have timezone offset")
            local=dt.astimezone(IST)
            if local.utcoffset()!=timedelta(hours=5,minutes=30):
                raise ValueError("Unexpected India timezone")
            if local.second or local.microsecond or local.minute%5!=0:
                raise ValueError("Only completed regular-grid 5-minute candle start timestamps")
            nums={}
            for key in ("open","high","low","close","volume"):
                try:v=float(item[key])
                except (ValueError,TypeError):raise ValueError("Invalid OHLCV") from None
                if not math.isfinite(v) or (v<=0 if key!="volume" else v<0):
                    raise ValueError("Nonfinite/invalid OHLCV")
                nums[key]=v
            if not nums["low"]<=min(nums["open"],nums["close"])<=max(nums["open"],nums["close"])<=nums["high"]:
                raise ValueError("Impossible intraday candle")
            sessions[local.date().isoformat()].append({"time":local,"values":nums})
            if sum(map(len,sessions.values()))>25000:raise ValueError("Too many intraday bars")
    if not sessions:raise ValueError("No actual intraday candles provided")
    return sessions,hashlib.sha256(f.read_bytes()).hexdigest()

def replay(path,symbol,*,max_loss_inr=1500.0,capital_inr=100000.0,
           friction_bps=16.0,bootstrap_paths=10000,seed=42):
    if not isinstance(bootstrap_paths,int) or isinstance(bootstrap_paths,bool) or not 1000<=bootstrap_paths<=100000:
        raise ValueError("Monte Carlo resampling paths must be 1000..100000")
    if not isinstance(seed,int) or isinstance(seed,bool):raise ValueError("Integer deterministic seed required")
    for v,name,lo,hi in [(max_loss_inr,"risk budget",1,1e7),(capital_inr,"capital",1000,1e9),
                         (friction_bps,"friction bps",0,500)]:
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi:
            raise ValueError("Invalid "+name)
    if max_loss_inr>capital_inr*.05:raise ValueError("Paper risk budget >5% of paper capital")
    sessions,source_sha=_read_bars(path,symbol)
    wins=losses=expired=0;rejected=0;records=[];no_setup=0
    for day,bars in sorted(sessions.items()):
        times=[b["time"] for b in bars]
        first=datetime.fromisoformat(day+"T09:15:00").replace(tzinfo=IST)
        expected=[first+timedelta(minutes=5*i) for i in range(75)]
        if times!=expected or len(bars)!=75:
            rejected+=1;continue
        # First 15 min opening range. Never inspect future beyond signal bar.
        hi=max(b["values"]["high"] for b in bars[:3])
        lo=min(b["values"]["low"] for b in bars[:3])
        if hi<=lo:rejected+=1;continue
        # Only generate a signal on a COMPLETED 5-minute candle, enter next OPEN.
        signal=None
        for i in range(3,48):
            if bars[i]["values"]["close"]>hi:
                signal=i;break
        if signal is None:
            no_setup+=1;continue
        entry_idx=signal+1
        entry=bars[entry_idx]["values"]["open"]
        stop=(hi+lo)/2
        risk=entry-stop
        if risk<=0 or risk/entry<0.001 or risk/entry>0.20:
            expired+=1;continue
        target=entry+risk # 1R, paper only
        # Full capital/risk cap; no leverage and no individual F&O lot assumption.
        quantity=min(int(max_loss_inr/risk),int(capital_inr/entry))
        if quantity<1:expired+=1;continue
        exit_px=bars[-1]["values"]["close"];reason="SESSION_CLOSE";exit_idx=74
        for i in range(entry_idx,75):
            candle=bars[i]["values"]
            # Both hit in same OHLC bar -> conservative stop, never assume first target.
            if candle["low"]<=stop:
                exit_px=stop;reason="STOP_OR_AMBIGUOUS";exit_idx=i;break
            if candle["high"]>=target:
                exit_px=target;reason="TARGET";exit_idx=i;break
        gross=quantity*(exit_px-entry)
        friction=quantity*(entry+exit_px)*friction_bps/10000.0
        net=gross-friction
        r_multiple=net/(quantity*risk)
        records.append({"day":day,"entry_bar":bars[entry_idx]["time"].isoformat(),
              "signal_bar":bars[signal]["time"].isoformat(),
              "exit_bar":bars[exit_idx]["time"].isoformat(),
              "qty_paper":quantity,"entry":entry,"stop_assumed":stop,"target_assumed":target,
              "exit_assumed":exit_px,"exit_reason":reason,
              "paper_net_pnl_inr":round(net,2),"net_R":round(r_multiple,5)})
        if net>0:wins+=1
        else:losses+=1
    observed=[r["net_R"] for r in records]
    rng=random.Random(seed)
    # Bootstrap resamples *only realised historical setups*; invalid as a
    # calibrated probability about unknown market regimes. Avoid empty evidence.
    boot=[]
    if observed:
        for _ in range(bootstrap_paths):
            sample=[observed[rng.randrange(len(observed))] for _ in range(len(observed))]
            boot.append(statistics.mean(sample))
        boot.sort()
    return {"engine":"FUNDTEX_INTRADAY_REPLAY_V1","symbol":symbol,
      "source_sha256":source_sha,"market_calendar":"NSE/BSE_REGULAR_SESSION_ONLY",
      "market_hours_ist":"09:15-15:30","bar_interval":"5m, 75 fully observed bars per valid session",
      "sample_quality":{"total_days":len(sessions),"valid_complete_sessions":len(sessions)-rejected,
                         "incomplete_or_offgrid_excluded":rejected,
                         "no_breakout":no_setup,"invalid_risk_excluded":expired},
      "evaluation":{"sample_sessions":len(sessions)-rejected,"matched_setup_sessions":len(records),
                    "historical_wins":wins,"historical_losses_or_flat":losses,
                    "average_net_R":round(statistics.mean(observed),5) if observed else None,
                    "historical_positive_fraction":round(wins/len(records),5) if records else None},
      "bootstrap":{"paths":bootstrap_paths,"seed":seed,"resamples_of_historical_setups_only":True,
                   "mean_R_interval_95":(round(boot[int(.025*(len(boot)-1))],5),
                                           round(boot[int(.975*(len(boot)-1))],5)) if boot else None,
                   "future_win_probability_calibrated":False},
      "method":"Long-only 15m opening range breakout, close confirmed, next 5m open paper fill, 1R target, conservative same-bar stop, paper fees",
      "trades":records[:500],
      "trading_enabled":False,"margin_or_derivatives_backtest":False,
      "stop_loss_guaranteed":False,"future_returns_predicted":False,
      "risk_disclaimers":["No slippage or halt guarantee; stop fill model is optimistic for gaps.",
                          "Historical bootstrap reuses observed days, not possible future shock regimes.",
                          "Intraday corporate actions, universe selection and official data timestamps not independently verified.",
                          "No actual brokerage option chain, realistic derivative lot/margin or P&L execution."]}
