"""Fundtex probabilistic forecast LAB: prequential, calibrated-on-past, no future lookups.

Returns one-day historical distribution forecasts, not trade recommendations.
This is an openly scored research experiment: actual outcomes are revealed only
after predictions have been generated using the historical prefix.
"""
from __future__ import annotations
import math
import random
import statistics
from .stats import _percentile

def _quantile(xs,q):
    return _percentile(xs,q)

def _brier_pairs(reports):
    return statistics.mean((x["p_up"]-x["outcome"])**2 for x in reports)

def _weighted_window(results,window,which):
    return results[-window:] if which=="recent" else results

def _bootstrap_skill(records, n_resamples=400, block_size=20, seed=42):
    """Moving-block bootstrap of score difference; heuristic uncertainty only."""
    n=len(records)
    if n < 30: return None
    rng=random.Random(seed)
    differences=[r["naive_brier"]-r["model_brier"] for r in records]
    out=[]
    for _ in range(n_resamples):
        chosen=[]
        while len(chosen)<n:
            at=rng.randrange(max(1,n-block_size+1))
            chosen.extend(differences[at:at+block_size])
        out.append(statistics.mean(chosen[:n]))
    out.sort()
    return {
        "mean_brier_improvement_ci95":[out[int(.025*(len(out)-1))],out[int(.975*(len(out)-1))]],
        "method":"moving-block bootstrap of daily naive-minus-model Brier loss; exploratory, serial dependence possible",
        "resamples":n_resamples,"block_size":block_size,"seed":seed
    }

def prequential(rows, *, window=252, seed=42, probability_margin=.10):
    if not 120<=window<=1000:
        raise ValueError("window must be 120..1000 observations")
    if not 0<=probability_margin<=0.49:
        raise ValueError("probability margin must be 0..0.49")
    if len(rows)<window+100 or len(rows)>25000:
        raise ValueError("Need at least window+100 and at most 25000 observations")
    dates=[r["date"] for r in rows]
    if dates!=sorted(set(dates)):
        raise ValueError("Dates must be unique chronological sessions")
    p=[float(row["close"]) for row in rows]
    if any(not math.isfinite(v) or v<=0 for v in p):
        raise ValueError("All prices must be positive and finite")
    returns=[p[j+1]/p[j]-1.0 for j in range(len(p)-1)]
    audits=[]
    scored=[]
    historical_correct=[]
    for t in range(window,len(p)-1):
        # t denotes price index at decision close; last allowed return is
        # returns[t-1] (price[t-1] to price[t]), never returns[t].
        history=returns[t-window:t]
        positive=sum(1 for v in history if v>0)
        pup=(positive+1)/(window+2)  # Laplace-smoothed empirical frequency
        lo,median,hi=(_quantile(history,q) for q in (.1,.5,.9))
        actual=returns[t]              # outcome observed AFTER forecast
        y=int(actual>0)
        model_brier=(pup-y)**2
        naive_brier=(.5-y)**2
        expanding=returns[:t]
        base_p=(sum(1 for v in expanding if v>0)+1)/(len(expanding)+2)
        baseline_brier=(base_p-y)**2
        q_ok=int(lo<=actual<=hi)
        selected=int(abs(pup-.5)>=probability_margin)
        pred=int(pup>=.5)
        record={"date":dates[t],"outcome_date":dates[t+1],"p_up":pup,
                "q10":lo,"q50":median,"q90":hi,"actual_next_return":actual,
                "outcome":y,"model_brier":model_brier,"naive_brier":naive_brier,
                "expanding_prior_brier":baseline_brier,
                "covered":q_ok,"selected":selected,
                "selected_correct":selected*int(pred==y)}
        scored.append(record)
        if len(audits)<5 or t>=len(p)-6:
            audits.append(record)
    N=len(scored)
    model_loss=statistics.mean(x["model_brier"] for x in scored)
    naive_loss=statistics.mean(x["naive_brier"] for x in scored)
    prior_loss=statistics.mean(x["expanding_prior_brier"] for x in scored)
    coverage=statistics.mean(x["covered"] for x in scored)
    acted=sum(x["selected"] for x in scored)
    selected_correct=sum(x["selected_correct"] for x in scored)
    skill_vs_half=1-model_loss/naive_loss
    skill_vs_prior=1-model_loss/prior_loss if prior_loss else None
    boot=_bootstrap_skill(scored,seed=seed)
    # Aggregate calibration bins: timestamps in each bin remain past-only.
    bins=[]
    for left in (0,.2,.4,.6,.8):
        subset=[r for r in scored if left<=r["p_up"]<(left+.2) or (left==.8 and r["p_up"]==1)]
        bins.append({"p_range":[left,left+.2],"samples":len(subset),
                     "mean_forecast":statistics.mean(r["p_up"] for r in subset) if subset else None,
                     "observed_up_frequency":statistics.mean(r["outcome"] for r in subset) if subset else None})
    last_hist=returns[-window:]
    current_p=(sum(1 for v in last_hist if v>0)+1)/(window+2)
    last_interval=[_quantile(last_hist,q) for q in (.1,.5,.9)]
    # Research credibility gate. Even PASS does not authorize trading:
    # confidence is rejected if no positive held-out Brier improvement.
    enough=N>=250
    empirical_coverage_ok=abs(coverage-.8)<=.07
    more_skill=skill_vs_half>0 and skill_vs_prior is not None and skill_vs_prior>0
    boot_positive=boot is not None and boot["mean_brier_improvement_ci95"][0]>0
    provisional=bool(enough and empirical_coverage_ok and more_skill and boot_positive)
    return {
        "engine":"FUNDTEX / CALIBRATION LAB v0.3",
        "market":"India (symbol and source supplied externally)",
        "as_of":dates[-1],"observations":len(rows),"evaluated_from":dates[window],
        "out_of_sample_days":N,"horizon":"next observed close-to-close session",
        "evaluation":"prequential / predictions from historical prefix only",
        "model":"Laplace-smoothed trailing positive-day frequency and 10/50/90 historical return quantiles",
        "benchmarks":["constant 50% up prior","expanding historical up frequency"],
        "brier":model_loss,"constant_half_brier":naive_loss,
        "expanding_prior_brier":prior_loss,
        "brier_skill_vs_constant_half":skill_vs_half,
        "brier_skill_vs_expanding_prior":skill_vs_prior,
        "nominal_interval_coverage":.8,
        "empirical_interval_coverage":coverage,
        "selected_decision_count":acted,
        "selected_fraction":acted/N,
        "selected_directional_hit_rate":selected_correct/acted if acted else None,
        "probability_margin":probability_margin,
        "bootstrap":boot,"reliability_bins":bins,
        "current_research_forecast":{
            "known_as_of":dates[-1],"p_next_day_up_empirical":current_p,
            "return_interval_10_50_90":last_interval,
            "directional_view":"UP_RESEARCH_HYPOTHESIS" if current_p>=.5+probability_margin
                               else "DOWN_RESEARCH_HYPOTHESIS" if current_p<=.5-probability_margin
                               else "ABSTAIN_INSUFFICIENT_EDGE",
            "is_a_calibrated_probability":False,
            "is_trading_recommendation":False
        },
        "gates":{
            "out_of_sample_size_sufficient":enough,
            "empirical_interval_coverage_acceptable":empirical_coverage_ok,
            "beat_both_directional_baselines":more_skill,
            "bootstrap_interval_excludes_nonpositive_improvement":boot_positive,
            "exploratory_distribution_model_pass":provisional,
            "license_corporate_actions_and_pit_certified":False,
            "authorized_for_live_trades":False
        },
        "audit_first_last":audits,
        "caveats":["Return quantiles and p-up are empirical historical estimates, not a proven or individualized market forecast.",
                   "Coverage and Brier scores use an archived series which may be incomplete or retrospectively adjusted.",
                   "Block-bootstrap significance does not correct multi-hypothesis selection or guarantee future skill.",
                   "Prices, dividend/split adjustments, survivorship, fees, latency and Indian market microstructure not validated.",
                   "No distribution forecast is authorized for execution or a client recommendation."]
    }
