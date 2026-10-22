"""Regime-falsification bench for the Fundtex strategy lab.

This manufactures SYNTHETIC adversarial OHLC sequences. Each experiment
performs training-only rule selection and chronological holdout evaluation.
Statistics are performance measurements of code under fictional generators,
NOT a real-market backtest or simulated forecast of Indian equity returns.
"""
from __future__ import annotations

import csv
from datetime import date,timedelta
import math
import random
import statistics
import tempfile
from pathlib import Path
from .strategy_lab import run

RULES = [
    {"name":"sma_cross","fast":10,"slow":50},
    {"name":"sma_cross","fast":20,"slow":80},
    {"name":"rsi_reversion","entry":30,"exit":70},
]
REGIMES = ("random_walk","bull_drift","bear_drift","mean_revert","volatility_shock")

def simulate_regimes(*, scenarios_per_regime=20, seed=42, sessions=540,
                     cost_bps=15, extra_cost_multiplier=4):
    if isinstance(scenarios_per_regime,bool) or not isinstance(scenarios_per_regime,int) or not 1<=scenarios_per_regime<=300:
        raise ValueError("scenarios_per_regime must be 1..300")
    if isinstance(seed,bool) or not isinstance(seed,int) or not 0<=seed<=2147483647:
        raise ValueError("seed must be 0..2147483647")
    if isinstance(sessions,bool) or not isinstance(sessions,int) or not 420<=sessions<=1200:
        raise ValueError("sessions must be 420..1200")
    if isinstance(cost_bps,bool) or not isinstance(cost_bps,(int,float)) or not math.isfinite(cost_bps) or not 0<=cost_bps<=500:
        raise ValueError("cost_bps must be finite in 0..500")
    if isinstance(extra_cost_multiplier,bool) or not isinstance(extra_cost_multiplier,(int,float)) or not math.isfinite(extra_cost_multiplier) or not 1<=extra_cost_multiplier<=10:
        raise ValueError("extra_cost_multiplier must be in 1..10")
    results={}
    with tempfile.TemporaryDirectory(prefix="fundtex-regime-") as root:
        sample=Path(root)/"synthetic.csv"
        for ridx,regime in enumerate(REGIMES):
            records=[]
            for trial in range(scenarios_per_regime):
                # Seeds derived from a stable pair (regime, trial). No RNG state
                # borrowed across experiments and no actual exchange dates.
                rng=random.Random(seed+100003*ridx+104729*trial)
                price=100.0
                log_anchor=math.log(100.0)
                with sample.open("w",newline="",encoding="utf-8") as f:
                    out=csv.writer(f)
                    out.writerow(("date","symbol","open","high","low","close","volume","source"))
                    for i in range(sessions):
                        normal=rng.gauss(0,1)
                        if regime=="random_walk":
                            daily=.012*normal
                        elif regime=="bull_drift":
                            daily=.001+.011*normal
                        elif regime=="bear_drift":
                            daily=-.001+.014*normal
                        elif regime=="mean_revert":
                            daily=.11*(log_anchor-math.log(price))+.012*normal
                        else:
                            daily=(.008 if i<sessions*.55 else .035)*normal
                            if i==int(sessions*.64):daily-=.22
                        # Any actual historical asset can have a different
                        # calendar/volatility path. This is not NSE data.
                        open_price=price*math.exp(.002*rng.gauss(0,1))
                        close=open_price*math.exp(daily)
                        hi=max(open_price,close)*1.001
                        lo=min(open_price,close)*.999
                        out.writerow(((date(2023,1,1)+timedelta(days=i)).isoformat(),
                                      "SYNTHETIC.NS",open_price,hi,lo,close,
                                      100000+i,"SYNTHETIC_FIXTURE"))
                        price=close
                spec={"candidates":RULES,"split_fraction":.7,
                      "cost_bps_per_position_change":float(cost_bps),
                      "minimum_train_sessions":120}
                report=run(sample,"SYNTHETIC.NS",spec)
                hold=report["holdout"]
                adverse=report["holdout_cost_stress"][-1]["holdout"] if extra_cost_multiplier==4 else None
                records.append({"selected":report["optimized_rule"],"training_net_excess":report["train"]["net_excess_over_buy_hold"],
                                "heldout_net_excess":hold["net_excess_over_buy_hold"],
                                "heldout_model_return":hold["net_total_return"],
                                "heldout_buyhold_return":hold["buy_hold_total_return"],
                                "drawdown":hold["max_drawdown"],
                                "trade_count":hold["number_of_position_changes"],
                                "holdout_after_4x_cost_net_excess":adverse["net_excess_over_buy_hold"] if adverse else None})
            vals=[x["heldout_net_excess"] for x in records]
            profitable=sum(x["heldout_net_excess"]>0 for x in records)
            p=profitable/len(records)
            # Wilson interval: describes synthetic-regime replications only.
            z=1.96
            den=1+z*z/len(records)
            centre=(p+z*z/(2*len(records)))/den
            half=z/den*math.sqrt(p*(1-p)/len(records)+z*z/(4*len(records)**2))
            results[regime]={
                "experiments":len(records),
                "train_candidate_count_per_experiment":len(RULES),
                "holdout_outperformance_rate":round(p,6),
                "holdout_outperformance_wilson_95pct":[round(max(0,centre-half),6),round(min(1,centre+half),6)],
                "mean_heldout_excess_return":round(statistics.mean(vals),6),
                "median_heldout_excess_return":round(statistics.median(vals),6),
                "worst_heldout_excess_return":round(min(vals),6),
                "worst_strategy_drawdown":round(min(x["drawdown"] for x in records),6),
                "false_edge_possible":True,
                "model_is_synthetic":True
            }
    return {
       "engine":"FUNDTEX_SYNTHETIC_REGIME_FALSIFICATION_v1",
       "seed":seed,"regimes":results,
       "total_independent_synthetic_histories":len(REGIMES)*scenarios_per_regime,
       "total_training_rule_evaluations":len(REGIMES)*scenarios_per_regime*len(RULES),
       "bars_per_synthetic_history":sessions,
       "strategy_rules":RULES,
       "cost_bps_per_position_change":float(cost_bps),
       "selection":"Preselected bounded candidate family, train only, chronological holdout",
       "market_data_provenance":"SYNTHETIC_FIXTURE_ONLY",
       "trading_signal":"NONE",
       "claim":"This bench measures code robustness under specified fictional price processes; never extrapolate its win frequency to India markets.",
       "research_only":True,"trading_authority":False
    }
