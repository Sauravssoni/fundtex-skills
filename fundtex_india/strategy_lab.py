"""Fundtex strategy research: explicit rule DSL, training-only selection, next-open walk-forward.

Read-only reproducible historical experimentation. No orders, account access,
survivorship adjustment, guaranteed alpha, or auto-tuned independent test.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import math
import statistics
from .chart_studio import prices

def _int(v, name, low, high):
    if isinstance(v,bool) or not isinstance(v,int) or not low<=v<=high:
        raise ValueError(f"{name}: expected integer in {low}..{high}")
    return v

def _float(v, name, low, high):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not low<=v<=high:
        raise ValueError(f"{name}: invalid finite value")
    return float(v)

def _strategy(item):
    if not isinstance(item,dict) or set(item)-{"name","fast","slow","entry","exit"}:
        raise ValueError("Strategy must be a restricted JSON object, not executable code")
    name=item.get("name")
    if name=="sma_cross":
        if set(item)!={"name","fast","slow"}:raise ValueError("SMA requires name,fast,slow")
        fast=_int(item["fast"],"fast",3,80)
        slow=_int(item["slow"],"slow",10,252)
        if fast>=slow:raise ValueError("fast SMA period must be shorter than slow")
        return {"name":name,"fast":fast,"slow":slow}
    if name=="rsi_reversion":
        if set(item)!={"name","entry","exit"}:raise ValueError("RSI requires name,entry,exit")
        entry=_int(item["entry"],"entry",5,45)
        leave=_int(item["exit"],"exit",50,95)
        if entry>=leave:raise ValueError("RSI buy trigger must be below exit trigger")
        return {"name":name,"entry":entry,"exit":leave}
    raise ValueError("Supported research rules: sma_cross or rsi_reversion")

def _rsi(closes):
    from .chart_studio import rsi
    return rsi(closes,14)

def _signals(rows, rule):
    close=[r["close"] for r in rows]
    if rule["name"]=="sma_cross":
        from .chart_studio import sma
        a=sma(close,rule["fast"]);b=sma(close,rule["slow"])
        return [int(x is not None and y is not None and x>y) for x,y in zip(a,b)]
    r=_rsi(close)
    position=0;signals=[]
    for value in r:
        if value is not None:
            if position==0 and value<rule["entry"]:position=1
            elif position==1 and value>rule["exit"]:position=0
        signals.append(position)
    return signals

def _max_dd(curve):
    peak=curve[0];worst=0.0
    for v in curve:
        peak=max(v,peak)
        worst=min(worst,v/peak-1)
    return worst

def _simulate(rows, signals, *, first_signal, last_signal, cost_bps):
    # Signal at close[i]; fill change at open[i+1]; earn open[i+1] -> open[i+2].
    pos=0;equity=1.0;benchmark=1.0;daily=[];bench_daily=[];turnovers=0
    curve=[1.0];bench_curve=[1.0];trade_dates=[]
    for i in range(first_signal,last_signal+1):
        desired=signals[i]
        turnover=abs(desired-pos)
        fill=rows[i+1]["open"];next_open=rows[i+2]["open"]
        gross=next_open/fill-1.0
        trading_cost=turnover*cost_bps/10000.0
        net=desired*gross-trading_cost
        if 1+net <= 0:raise ValueError("Gross return/cost combination wipes out research account")
        equity*=1+net;benchmark*=1+gross
        daily.append(net);bench_daily.append(gross)
        curve.append(equity);bench_curve.append(benchmark)
        if turnover:trade_dates.append(rows[i+1]["date"])
        turnovers+=turnover
        pos=desired
    volatility=statistics.stdev(daily)*math.sqrt(252) if len(daily)>1 else 0
    avg=statistics.mean(daily)
    sharpe=avg*252/volatility if volatility>0 else None
    q=sorted(daily);k=max(1,math.ceil(len(q)*.05))
    return {"sessions":len(daily),"equity_multiplier":round(equity,8),
            "net_total_return":round(equity-1,8),
            "buy_hold_total_return":round(benchmark-1,8),
            "net_excess_over_buy_hold":round(equity-benchmark,8),
            "max_drawdown":round(_max_dd(curve),8),
            "annualized_realized_volatility":round(volatility,8),
            "annualized_sharpe_zero_riskfree":round(sharpe,6) if sharpe is not None else None,
            "historical_worst5pct_mean_daily_return":round(statistics.mean(q[:k]),8),
            "number_of_position_changes":turnovers,
            "trade_dates":trade_dates[:60],
            "trade_dates_truncated":len(trade_dates)>60,
            "last_signal_date":rows[last_signal]["date"],
            "equity_curve": [round(x,6) for x in curve],
            "benchmark_curve": [round(x,6) for x in bench_curve]}

def run(price_csv, symbol, spec):
    if not isinstance(spec,dict) or set(spec)-{"candidates","split_fraction","cost_bps_per_position_change","minimum_train_sessions"}:
        raise ValueError("Strategy research specification has unknown fields")
    history=prices(price_csv,symbol)
    if not history["ohlc"]:
        raise ValueError("Genuine open/high/low/close needed for next-open fills; never fabricate OHLC")
    rows=history["rows"]
    if len(rows)<240:raise ValueError("At least 240 OHLC observations required for robust train and untouched holdout")
    if len(rows)>20000:raise ValueError("Large histories require an authorized downsample")
    candidates=spec.get("candidates")
    if not isinstance(candidates,list) or not 1<=len(candidates)<=32:
        raise ValueError("Supply 1..32 bounded candidate rules")
    rule_candidates=[_strategy(x) for x in candidates]
    if len({str(x) for x in rule_candidates})!=len(rule_candidates):
        raise ValueError("Duplicate strategies do not count as independent trials")
    split=_float(spec.get("split_fraction",.7),"split_fraction",.6,.85)
    costs=_float(spec.get("cost_bps_per_position_change",15),"cost_bps_per_position_change",0,500)
    train_min=_int(spec.get("minimum_train_sessions",120),"minimum_train_sessions",100,1000)
    boundary=int(len(rows)*split)
    # Initial warmup is excluded from both training and held-out score.
    warmup=max(40,max((x["slow"] if x["name"]=="sma_cross" else 15) for x in rule_candidates))
    train_first=warmup
    train_last=boundary-3
    # Holdout is chronologically later; no holdout statistic is used in model selection.
    test_first=boundary-1
    test_last=len(rows)-3
    if train_last-train_first+1<train_min or test_last-test_first+1<40:
        raise ValueError("Too few independent train/holdout sessions after indicator warmup")
    trials=[]
    for rule in rule_candidates:
        signals=_signals(rows,rule)
        training=_simulate(rows,signals,first_signal=train_first,last_signal=train_last,cost_bps=costs)
        # Pre-registered conservative selection: train-only net excess over buy-and-hold,
        # minus turnover penalty already included by fee assumption.
        score=training["net_excess_over_buy_hold"]
        trials.append({"rule":rule,"train_score":score,"train":training,"signals":signals})
    # Deterministic tie-breaking by position, never by holdout score.
    winner=max(range(len(trials)),key=lambda i:(trials[i]["train_score"],-i))
    chosen=trials[winner]
    holdout=_simulate(rows,chosen["signals"],first_signal=test_first,last_signal=test_last,cost_bps=costs)
    stress=[{"cost_multiplier":m,"holdout":_simulate(rows,chosen["signals"],
               first_signal=test_first,last_signal=test_last,cost_bps=costs*m)}
            for m in (2,4)]
    observed="NO_OBSERVED_NET_EXCESS" if holdout["net_excess_over_buy_hold"]<=0 else "DESCRIPTIVE_NET_OUTPERFORMANCE_NOT_PROVEN_ALPHA"
    return {
        "engine":"FUNDTEX_HISTORICAL_STRATEGY_LAB_v1",
        "symbol":history["symbol"],"data_quality":history["data_quality"],
        "source_sha256":history["source_sha256"],
        "last_history_date":history["last_observation"],
        "history_observations":len(rows),"train_end":rows[boundary-1]["date"],
        "holdout_first_fill_date":rows[boundary]["date"],
        "test_period_untouched_during_selection":True,
        "optimized_rule":chosen["rule"],
        "selected_from_trials":len(trials),
        "candidate_train_scores":[{"rule":x["rule"],"net_excess":x["train_score"],
                                   "trades":x["train"]["number_of_position_changes"]} for x in trials],
        "train":chosen["train"],"holdout":holdout,
        "holdout_cost_stress":stress,
        "cost_bps_per_change_assumed":costs,
        "status":observed,
        "execution_assumption":"Completed close signal; next real OHLC open fill; hypothetical next-open to following-open return",
        "warnings":[
            "NOT a live test, accurate return forecast, advice, or exchange-certified price verification",
            "Corporate action adjustments, delisted securities, Indian charges/STT/GST/stamp, impact and taxes require a separate licensed instrument-appropriate ledger",
            "Training-selected parameters may overfit even when holdout untouched; statistical significance and forward paper-trading not established",
            "Long-or-cash only; no leverage, margin, shorting, dividends, dynamic capital allocation or derivative physical delivery",
            "RSI Wilder vs source data can vary; use consistent close history and indicator definitions"
        ],
        "research_only":True,"trading_authority":False
    }
