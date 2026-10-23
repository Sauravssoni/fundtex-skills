"""Retrospective, non-executable, unlevered Kronos long/flat placebo test.

Inputs are already-produced point-in-time walkforward predictions. This NEVER
re-forecasts or places market orders; reference entry/exit prices remain
UNVERIFIED historical observations and all frictions illustrative assumptions.
"""
from __future__ import annotations
from hashlib import sha256
import json
import math
from pathlib import Path
import random
from .kronos_lab import bars_from_csv

def assess(report, csv_path, symbol, *,threshold_bps=0, cost_bps=(0,20,50), permutations=1000,seed=42):
    if not isinstance(report,dict) or report.get("engine")!="FUNDTEX_KRONOS_CHALLENGER_WALKFORWARD_V1":
        raise ValueError("Actual FundTex Kronos historical cutoff report required")
    data=bars_from_csv(csv_path,symbol)
    if report.get("source_sha256")!=data["source_sha256"] or report.get("symbol")!=data["symbol"]:
        raise ValueError("Source SHA/ticker mismatch; reject paper comparisons")
    if any(isinstance(x,bool) or not isinstance(x,int) for x in (threshold_bps,permutations,seed)):
        raise ValueError("No coerced risk parameters")
    if not 0<=threshold_bps<=500 or not 10<=permutations<=10000:
        raise ValueError("Paper settings outside vetted limits")
    if not isinstance(cost_bps,(tuple,list)) or not cost_bps or len(cost_bps)>10 or any(
          isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) or not 0<=x<=500 for x in cost_bps):
        raise ValueError("Hypothetical round-trip costs must be finite 0..500 bps")
    windows=report.get("cutoff_diagnostics")
    if not isinstance(windows,list) or len(windows)<3 or len(windows)>60:
        raise ValueError("Expected chronological model prediction windows")
    prices={r["date"]:r for r in data["rows"]}
    all_dates=[r["date"] for r in data["rows"]]
    trials=[];last_exit=None
    for block in windows:
        origin=block["forecast_at_close"];start=block["first_outcome"];end=block["last_outcome"]
        if origin not in prices or start not in prices or end not in prices:
            raise ValueError("Unmatched history window dates")
        oi=all_dates.index(origin);si=all_dates.index(start);ei=all_dates.index(end)
        if si!=oi+1 or ei<si or (last_exit and si<=last_exit):
            raise ValueError("Overlapping/noncausal paper windows")
        last_exit=ei
        predicted=block.get("models",{}).get("challenger",{}).get("predicted_close")
        if not isinstance(predicted,list) or len(predicted)!=ei-si+1:
            raise ValueError("Prediction horizon unverified")
        for x in predicted:
            if not isinstance(x,(float,int)) or isinstance(x,bool) or not math.isfinite(x) or x<=0:
                raise ValueError("Invalid recorded forecast")
        anchor=prices[origin]["close"]
        signal=(predicted[-1]/anchor-1)*10000>threshold_bps
        # Entry is next actual OHLC open. It was NOT known at signal creation,
        # only used later to evaluate a hypothetical fill with no bid/ask data.
        entry=prices[start]["open"];exit_=prices[end]["close"]
        gross=exit_/entry-1
        trials.append({"decision_as_of":origin,"entry_session":start,"exit_session":end,
                       "signal":"HYPOTHETICAL_LONG" if signal else "CASH",
                       "origin_close":anchor,"next_session_open":entry,"exit_observed_close":exit_,
                       "model_predicted_exit_close":predicted[-1],
                       "gross_long_return":gross,"gross_model_strategy_return":gross if signal else 0,
                       "trade_executed":False})
    if len(trials)<3:raise ValueError("Need >=3 independent paper windows")
    flags=[r["signal"]=="HYPOTHETICAL_LONG" for r in trials]
    baseline=[r["gross_long_return"] for r in trials]
    def scenario(cost):
        model=[(r if held else 0)-float(cost)/10000*(1 if held else 0)
                 for r,held in zip(baseline,flags)]
        always=[r-float(cost)/10000 for r in baseline]
        def stats(rs):
            equity=1.;peak=1.;maxdd=0.
            for x in rs:
                equity*=max(0,1+x)
                peak=max(peak,equity)
                maxdd=max(maxdd,1-equity/peak)
            return {"compounded_window_return":equity-1,"worst_window_return":min(rs),
                    "best_window_return":max(rs),"max_window_drawdown":maxdd}
        return {"assumed_roundtrip_cost_bps":cost,
                "kronos_long_cash":stats(model),"always_long":stats(always),
                "number_of_hypothetical_long_exposures":sum(flags)}
    # Shuffle same number of signals across nonoverlapping historical windows.
    # A null test, not real market alpha or statistical confidence for 12 windows.
    rng=random.Random(seed)
    observed=sum((r if f else 0) for r,f in zip(baseline,flags))
    placebo=[]
    for _ in range(permutations):
        moved=flags[:]
        rng.shuffle(moved)
        placebo.append(sum(r if f else 0 for r,f in zip(baseline,moved)))
    placebo.sort()
    ge=sum(x>=observed for x in placebo)
    return {"engine":"FUNDTEX_KRONOS_PAPER_ONLY_DECISION_FALSIFIER_V1",
        "symbol":data["symbol"],"source_sha256":data["source_sha256"],
        "source_quality":data["source_quality"],"as_of":data["end"],
        "model_backend":report.get("backend_label"),
        "pretrained_contamination_unknown":True,"trade_execution":False,
        "broker_orders":0,"shorting":False,"leverage":0,
        "threshold_bps_predeclared":threshold_bps,
        "windows":len(trials),"model_long_windows":sum(flags),
        "cost_scenarios":[scenario(c) for c in cost_bps],
        "shuffle_null":{"permutations":permutations,"seed":seed,
            "one_sided_placebo_frequency_ge_observed":ge/permutations,
            "notes":"Shuffled fixed number of signals; temporal dependence and model pretraining leakage invalidate formal significance claims"},
        "limit":"Hypothetical next-open to horizon-close fills; no market depth, brokerage, STT, stamp duty, spreads, slippage, holidays or live option chain verified",
        "conclusion":"UNVALIDATED_HISTORICAL_PAPER_RESEARCH_NOT_EXECUTABLE_ALPHA",
        "decision_windows":trials}
