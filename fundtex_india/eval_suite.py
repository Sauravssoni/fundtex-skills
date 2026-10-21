"""Reproducible synthetic market-regime adversarial evaluation of Fundtex probabilistic forecasts.

Never report these generated series as real NSE/BSE or proof of predictive alpha.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import random
import statistics
from .forecast import prequential


REGIMES = ("random_walk", "bull_drift", "bear_drift", "mean_reversion", "volatility_cluster", "jump_shocks")


def make_scenario(regime: str, *, sessions: int, seed: int):
    if regime not in REGIMES:
        raise ValueError("Unknown stress regime")
    if not 380 <= sessions <= 5000:
        raise ValueError("380..5000 sessions required")
    rng=random.Random(seed)
    start=dt.date(2018,1,1)
    price=100.
    latent=0.
    rows=[]
    for day in range(sessions):
        z=rng.gauss(0,1)
        if regime=="random_walk":
            logret=.012*z
        elif regime=="bull_drift":
            logret=.0006+.012*z
        elif regime=="bear_drift":
            logret=-.0006+.012*z
        elif regime=="mean_reversion":
            previous=latent
            latent=0.90*latent+.015*z
            logret=latent-previous
        elif regime=="volatility_cluster":
            shock=.032 if (day//30)%4==2 else .006
            logret=.0001+shock*z
        else:
            logret=.0004+.01*z + (-.16 if day>0 and day%113==0 else 0)
        price*=math.exp(logret)
        rows.append({"date":(start+dt.timedelta(days=day)).isoformat(),"close":price})
    return rows


def stress_suite(*, scenarios=36, sessions=540, seed=42, window=120):
    if not 6<=scenarios<=600 or scenarios%6 or not 380<=sessions<=5000:
        raise ValueError("scenarios must be a 6-multiple between 6 and 600; sessions 380..5000")
    if window<120 or sessions<window+100:
        raise ValueError("Forecast sample too short")
    results=[]
    for i in range(scenarios):
        regime=REGIMES[i%len(REGIMES)]
        runseed=seed+i*7919
        rows=make_scenario(regime,sessions=sessions,seed=runseed)
        report=prequential(rows,window=window,seed=runseed)
        results.append({
            "scenario_id":i+1,"seed":runseed,"regime":regime,
            "oos_days":report["out_of_sample_days"],
            "brier_skill_vs_half":report["brier_skill_vs_constant_half"],
            "brier_skill_vs_expanding_prior":report["brier_skill_vs_expanding_prior"],
            "interval_coverage":report["empirical_interval_coverage"],
            "selected_fraction":report["selected_fraction"],
            "passed_model_gate":report["gates"]["exploratory_distribution_model_pass"]
        })
    skills=[r["brier_skill_vs_expanding_prior"] for r in results]
    by_regime={
        name:{
            "scenarios":sum(r["regime"]==name for r in results),
            "mean_brier_skill_vs_expanding":statistics.mean(r["brier_skill_vs_expanding_prior"] for r in results if r["regime"]==name),
            "mean_interval_coverage":statistics.mean(r["interval_coverage"] for r in results if r["regime"]==name),
            "model_gates_passed":sum(r["passed_model_gate"] for r in results if r["regime"]==name)
        } for name in REGIMES
    }
    params={"scenarios":scenarios,"sessions_per_scenario":sessions,"seed":seed,"window":window,"regimes":list(REGIMES)}
    return {
        "product":"Fundtex Financial Intelligence | Syntheon Technology",
        "suite":"v0.4 adverse regime research evaluation",
        "source":"SYNTHETIC_GENERATOR_NOT_MARKET_DATA",
        "input_config_sha256":hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest(),
        "parameters":params,
        "total_synthetic_observations":scenarios*sessions,
        "total_prequential_forecast_scores":sum(r["oos_days"] for r in results),
        "mean_brier_skill_vs_expanding_prior":statistics.mean(skills),
        "median_brier_skill_vs_expanding_prior":statistics.median(skills),
        "research_gates_passed":sum(r["passed_model_gate"] for r in results),
        "research_gates_failed":sum(not r["passed_model_gate"] for r in results),
        "by_regime":by_regime,"scenario_results":results,
        "caveats":[
            "All data are manufactured synthetic price paths, never Indian exchange observations.",
            "Forecast gate pass here does not establish trading alpha or regulated advisory suitability.",
            "No direct equity trades, broker execution, options, fees, corporate actions, or real-world market impact.",
            "Never optimize on these evaluation seeds or silently deploy model changes from their results."
        ]
    }
