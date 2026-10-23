"""Read-only option spread candidate enumerator from an approved, timestamped chain CSV.

Candidate ranking is model payoff arithmetic, NOT advice/alpha or broker margin.
Quotes are conservative sell-at-bid, buy-at-ask and explicitly UNVERIFIED input.
"""
from __future__ import annotations
from datetime import date,datetime,timezone
import csv
from hashlib import sha256
import math
from pathlib import Path
from .options_lab import evaluate

def _num(v, name, minimum=0.0):
    if isinstance(v,bool):
        raise ValueError(f"Invalid {name}")
    try:f=float(v)
    except (ValueError,TypeError):raise ValueError(f"Invalid {name}") from None
    if not math.isfinite(f) or f<minimum:raise ValueError(f"Invalid {name}")
    return f

def _date(text):
    try:return date.fromisoformat(text)
    except (ValueError,TypeError):raise ValueError("All dates must be YYYY-MM-DD") from None

def propose(chain_csv, config):
    if not isinstance(config,dict):
        raise ValueError("Options builder config must be a JSON object")
    required={"underlying","spot","lot_size","valuation_date","expiry_date","structure",
              "min_width","max_width","max_risk_inr"}
    allowed=required|{"top_n","max_age_days","rates","annualized_volatility","annual_risk_free","seed","paths",
              "analysis_at_utc","max_snapshot_age_seconds","max_quote_spread_bps",
              "min_top_quantity","min_day_volume","min_open_interest"}
    if not required<=set(config) or set(config)-allowed:
        raise ValueError("Explicit underlying, spot, lot size, valuation/expiry, structure, widths and risk budget required")
    if config["structure"] not in ("bull_put_credit","bear_call_credit"):
        raise ValueError("Only defined-risk credit verticals supported in chain builder")
    symbol=config["underlying"]
    if not isinstance(symbol,str) or not 1<=len(symbol)<=50 or not all(c.isascii() and (c.isalnum() or c in "-_.^") for c in symbol):
        raise ValueError("Symbol must be a short verified contract underlying")
    asof=_date(config["valuation_date"])
    expiry=_date(config["expiry_date"])
    if expiry<asof or (expiry-asof).days>365:
        raise ValueError("Expiry outside research range")
    lot=config["lot_size"]
    if isinstance(lot,bool) or not isinstance(lot,int) or not 1<=lot<=100000:
        raise ValueError("Lot size must be explicitly supplied")
    spot=_num(config["spot"],"spot",0.001)
    minimum=_num(config["min_width"],"min_width",0.001)
    maximum=_num(config["max_width"],"max_width",minimum)
    budget=_num(config["max_risk_inr"],"max_risk_inr",0.01)
    limit=config.get("top_n",5)
    if isinstance(limit,bool) or not isinstance(limit,int) or not 1<=limit<=15:
        raise ValueError("top_n range is 1..15")
    max_age=config.get("max_age_days",3)
    if isinstance(max_age,bool) or not isinstance(max_age,int) or not 0<=max_age<=7:
        raise ValueError("max_age_days range is 0..7")
    def positive_integer_setting(key, default, maximum):
        v=config.get(key,default)
        if isinstance(v,bool) or not isinstance(v,int) or not 0<=v<=maximum:
            raise ValueError(key+" must be a bounded non-negative integer")
        return v
    max_snap_age=positive_integer_setting("max_snapshot_age_seconds",180,86400)
    max_spread=_num(config.get("max_quote_spread_bps",10000),"max_quote_spread_bps")
    if max_spread>100000:raise ValueError("Spread bps outside approved bounds")
    min_qty=positive_integer_setting("min_top_quantity",0,10000000)
    min_volume=positive_integer_setting("min_day_volume",0,2000000000)
    min_oi=positive_integer_setting("min_open_interest",0,2000000000)
    analysis_at=None
    if "analysis_at_utc" in config:
        try:analysis_at=datetime.fromisoformat(config["analysis_at_utc"].replace("Z","+00:00"))
        except (ValueError,TypeError,AttributeError):raise ValueError("Invalid analysis_at_utc") from None
        if analysis_at.tzinfo is None:
            raise ValueError("analysis_at_utc must include UTC offset")
        analysis_at=analysis_at.astimezone(timezone.utc)
    source=Path(chain_csv)
    if not source.is_file() or source.stat().st_size>1_000_000:
        raise ValueError("Approved chain CSV absent or too large")
    rows=[]
    filtered={"spread":0,"liquidity":0}
    snapshots=set()
    sources=set()
    ids=set()
    quote_timestamp_count=0
    needed={"symbol","expiry","kind","strike","bid","ask","lot_size","as_of"}
    with source.open(newline="",encoding="utf-8-sig") as handle:
        reader=csv.DictReader(handle)
        if not needed <= set(reader.fieldnames or []):
            raise ValueError("Chain CSV requires symbol, expiry, kind, strike, bid, ask, lot_size, as_of")
        for row in reader:
            if row["symbol"]!=symbol or row["expiry"]!=expiry.isoformat():continue
            if row["kind"] not in ("call","put"):raise ValueError("Unknown option type")
            quote_time=_date(row["as_of"])
            if quote_time>asof or (asof-quote_time).days>max_age:
                raise ValueError("Options quote snapshot is stale or future-dated")
            if int(row["lot_size"])!=lot:raise ValueError("Unverified lot-size mismatch in option chain")
            strike=_num(row["strike"],"strike",0.001)
            bid=_num(row["bid"],"bid",0.0)
            ask=_num(row["ask"],"ask",0.001)
            if bid>ask:raise ValueError("Impossible bid/ask spread")
            origin=(row.get("source") or "UNATTRIBUTED_APPROVED_CSV").strip()
            snapshot=(row.get("snapshot_id") or "").strip()
            captured=(row.get("quote_captured_utc") or "").strip()
            sources.add(origin)
            if origin.startswith("DHAN_"):
                if not snapshot or not captured or analysis_at is None:
                    raise ValueError("Dhan snapshot must have a unique receipt hash, capture timestamp and research analysis_at_utc")
            if snapshot:
                snapshots.add(snapshot)
            if captured:
                quote_timestamp_count+=1
                try:quote_dt=datetime.fromisoformat(captured.replace("Z","+00:00"))
                except ValueError:raise ValueError("Invalid timestamp in option-chain observation") from None
                if quote_dt.tzinfo is None:raise ValueError("Provider capture timestamp must carry timezone")
                if analysis_at is not None:
                    age=(analysis_at-quote_dt.astimezone(timezone.utc)).total_seconds()
                    if age<0 or age>max_snap_age:
                        raise ValueError("Options snapshot is future-dated or too old for this research")
            if row.get("security_id"):
                contract_id=row["security_id"].strip()
                if not contract_id.isdecimal() or int(contract_id)<=0 or contract_id in ids:
                    raise ValueError("Invalid or duplicated provider contract security_id")
                ids.add(contract_id)
            spread_bps=10000*(ask-bid)/((bid+ask)/2)
            if spread_bps>max_spread:
                filtered["spread"]+=1
                continue
            liquidity={}
            for attr,name in (("bid_qty","bid displayed size"),("ask_qty","ask displayed size"),
                              ("volume","day volume"),("open_interest","open interest")):
                raw=row.get(attr)
                if raw is None or raw=="":
                    if (attr in ("bid_qty","ask_qty") and min_qty>0) or (attr=="volume" and min_volume>0) or (attr=="open_interest" and min_oi>0):
                        raise ValueError("Required provider liquidity field missing: "+name)
                    liquidity[attr]=None
                    continue
                number=_num(raw,name)
                liquidity[attr]=number
            if (min_qty>0 and (liquidity["bid_qty"]<min_qty or liquidity["ask_qty"]<min_qty)) or (
                min_volume>0 and liquidity["volume"]<min_volume) or (min_oi>0 and liquidity["open_interest"]<min_oi):
                filtered["liquidity"]+=1
                continue
            rows.append({"kind":row["kind"],"strike":strike,"bid":bid,"ask":ask,
                         "as_of":row["as_of"],"spread_bps":round(spread_bps,5),
                         "bid_qty":liquidity["bid_qty"],"ask_qty":liquidity["ask_qty"],
                         "volume":liquidity["volume"],"open_interest":liquidity["open_interest"]})
            if len(rows)>100:
                raise ValueError("Limit chain to 100 valid contracts per expiry")
    if len(snapshots)>1 or len(sources)>1:
        raise ValueError("Mixed option-chain snapshots or sources; cannot infer simultaneous fills")
    if len(rows)<2:raise ValueError("Insufficient matching approved chain observations after liquidity gates")
    if len({(x["kind"],x["strike"]) for x in rows})!=len(rows):
        raise ValueError("Duplicate strike/kind quotes; no arbitrary first-row selection")
    kind="put" if config["structure"]=="bull_put_credit" else "call"
    candidates=sorted((x for x in rows if x["kind"]==kind),key=lambda x:x["strike"])
    if len(candidates)>50:raise ValueError("Too many strike pairs, filter chain on explicit range")
    variants=[]
    for j,short in enumerate(candidates):
        for i,long in enumerate(candidates):
            if (config["structure"]=="bull_put_credit" and not long["strike"]<short["strike"]) or (
                config["structure"]=="bear_call_credit" and not long["strike"]>short["strike"]):
                continue
            width=abs(long["strike"]-short["strike"])
            if not minimum<=width<=maximum:continue
            if short["bid"]<=long["ask"]:continue  # no executable hypothetical net credit
            spec={"underlying":symbol,"spot":spot,"lot_size":lot,
                  "valuation_date":asof.isoformat(),"expiry_date":expiry.isoformat(),
                  "legs":[{"kind":kind,"side":"sell","strike":short["strike"],"premium":short["bid"],"lots":1},
                          {"kind":kind,"side":"buy","strike":long["strike"],"premium":long["ask"],"lots":1}],
                  "max_risk_inr":budget,"require_defined_risk":True,
                  "data_quality":"USER_SUPPLIED_OPTIONS_CHAIN_UNVERIFIED"}
            if "rates" in config:spec["rates"]=config["rates"]
            try:trial=evaluate(spec)
            except ValueError:continue
            max_loss=trial["geometry"]["max_model_loss_inr"]
            max_gain=trial["geometry"]["max_model_profit_inr"]
            if max_loss is None or max_gain is None or max_loss<=0 or max_gain<=0:continue
            ratio=max_gain/max_loss
            variants.append((ratio,spec,trial))
            if len(variants)>1500:raise ValueError("Too many option pair candidates")
    variants.sort(key=lambda x:(-x[0], x[1]["legs"][0]["strike"], x[1]["legs"][1]["strike"]))
    selected=[]
    for score,spec,trial in variants[:limit]:
        if "annualized_volatility" in config:
            for k in ("annualized_volatility","annual_risk_free","seed","paths"):
                if k in config:spec[k]=config[k]
            trial=evaluate(spec)
        stress=[{"underlying":round(spot*(1+step),3),
                 "entry_cost_included_expiry_model_pnl_inr":round(
                    trial["opening_net_premium_credit_inr"]-trial["opening_total_cost_inr"]
                    +sum((1 if leg["side"]=="buy" else -1)*leg["lots"]*lot*
                      (max(spot*(1+step)-leg["strike"],0) if leg["kind"]=="call"
                       else max(leg["strike"]-spot*(1+step),0)) for leg in spec["legs"]),2)}
                for step in (-.10,-.05,0,.05,.10)]
        selected.append({
            "short_strike":spec["legs"][0]["strike"],"long_strike":spec["legs"][1]["strike"],
            "short_fill_assumed_bid":spec["legs"][0]["premium"],
            "long_fill_assumed_ask":spec["legs"][1]["premium"],
            "modeled_reward_to_max_intrinsic_loss":round(score,6),
            "max_model_profit_inr":trial["geometry"]["max_model_profit_inr"],
            "max_model_loss_inr":trial["geometry"]["max_model_loss_inr"],
            "opening_costs_inr":trial["opening_total_cost_inr"],
            "bid_ask_entry_is_only_a_quote_not_an_executable_fill":True,
            "simultaneous_leg_execution_verified":False,
            "break_even":trial["geometry"]["break_even_underlying_prices"],
            "stress_examples":stress,
            "scenario_simulation":trial.get("scenario_simulation"),
            "theoretical_greeks":trial.get("illustrative_greeks"),
        })
    return {"engine":"FUNDTEX_READ_ONLY_OPTION_SPREAD_BUILDER_v1",
            "underlying":symbol,"structure":config["structure"],
            "valuation_date":asof.isoformat(),"expiry":expiry.isoformat(),
            "user_supplied_lot_size":lot,"spot_user_supplied":spot,
            "input_file_sha256":sha256(source.read_bytes()).hexdigest(),
            "chain_matches":len(candidates),"evaluated_positive_credit_pairs":len(variants),
            "source_provenance":sorted(sources),
            "single_snapshot_id":next(iter(snapshots)) if len(snapshots)==1 else None,
            "captured_quote_timestamps_count":quote_timestamp_count,
            "research_analysis_timestamp_utc":analysis_at.isoformat() if analysis_at else None,
            "liquidity_filters":{"maximum_individual_quote_spread_bps":max_spread,
                                 "minimum_displayed_top_quantity":min_qty,
                                 "minimum_day_volume":min_volume,
                                 "minimum_open_interest":min_oi,
                                 "excluded":filtered},
            "eligible_candidates":selected,
            "candidate_ordering":"THEORETICAL_ENTRY_COST_ADJUSTED_GAIN_TO_MAX_INTRINSIC_LOSS_NOT_PREDICTIVE",
            "quote_data_quality":"USER_SUPPLIED_OPTIONS_CHAIN_UNVERIFIED",
            "market_margin_verified":False,"licensed_quote_verified":False,
            "expiry_exercise_stt_included":False,"actual_defined_loss_guaranteed":False,
            "research_only":True,"trading_authority":False,
            "warnings":["No historical options chain, exchange live authorization, Greeks/volatility calibration or execution quality guaranteed",
                        "Bid/ask are user-provided indications; live multi-leg simultaneous fills and margin relief unverified",
                        "Physical settlement, exercise STT, slippage, closure costs and applicable broker limits may change actual losses",
                        "Largest modeled credit/loss ratio is not a recommendation; the trade may be deeply in the money or infeasible"]}
