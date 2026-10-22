"""Read-only option spread candidate enumerator from an approved, timestamped chain CSV.

Candidate ranking is model payoff arithmetic, NOT advice/alpha or broker margin.
Quotes are conservative sell-at-bid, buy-at-ask and explicitly UNVERIFIED input.
"""
from __future__ import annotations
from datetime import date
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
    allowed=required|{"top_n","max_age_days","rates","annualized_volatility","annual_risk_free","seed","paths"}
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
    source=Path(chain_csv)
    if not source.is_file() or source.stat().st_size>1_000_000:
        raise ValueError("Approved chain CSV absent or too large")
    rows=[]
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
            rows.append({"kind":row["kind"],"strike":strike,"bid":bid,"ask":ask,"as_of":row["as_of"]})
            if len(rows)>100:
                raise ValueError("Limit chain to 100 valid contracts per expiry")
    if len(rows)<2:raise ValueError("Insufficient matching approved chain observations")
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
