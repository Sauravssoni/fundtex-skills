"""Fundtex GOD EYE: transparent time-causal price-signal evaluation, research only."""
from __future__ import annotations
import math
import statistics
from .stats import drawdown

METHODS=("momentum20","reversion5","trend20x60","breakout20")

def signal(p,t,method):
    if t<60:
        return 0
    if method=="momentum20":
        return int(p[t]>p[t-20] and p[t]>sum(p[t-20:t])/20)
    if method=="reversion5":
        return int(p[t]<p[t-5] and p[t]>sum(p[t-60:t])/60)
    if method=="trend20x60":
        return int(sum(p[t-19:t+1])/20>sum(p[t-59:t+1])/60)
    if method=="breakout20":
        return int(p[t]>max(p[t-20:t]))
    raise ValueError("Unknown strategy")

def metrics(returns):
    nav=[1.]
    for r in returns:
        nav.append(nav[-1]*(1+r))
    volatility=statistics.stdev(returns) if len(returns)>1 else 0
    return {"total_return":nav[-1]-1,"maximum_drawdown":drawdown(nav),
            "annualized_volatility":volatility*math.sqrt(252),
            "annualized_sharpe_approx":statistics.mean(returns)*math.sqrt(252)/volatility if volatility else None}

def trailing_net(p,model,end,lookback,cost):
    previous=0
    nav=1.
    for j in range(end-lookback,end):
        position=signal(p,j,model)
        step=position*(p[j+1]/p[j]-1)-cost*abs(position-previous)
        nav*=1+step
        previous=position
    if previous:
        nav*=1-cost
    return nav-1

def walkforward(rows,min_train=120,lookback=60,cost_bps=12):
    """At decision t, train from outcomes dated <=t only. No broker execution."""
    if not 120<=min_train<=3000 or not 40<=lookback<=2000 or min_train<lookback+60:
        raise ValueError("Invalid warmup/training split")
    if not 0<=cost_bps<=1000:
        raise ValueError("Invalid one-way basis-point cost")
    if not min_train+30<=len(rows)<=25000:
        raise ValueError("Need min_train+30 through 25,000 closing observations")
    dates=[x["date"] for x in rows]
    if dates!=sorted(set(dates)):
        raise ValueError("Observations must be unique and sorted")
    p=[float(x["close"]) for x in rows]
    if any(not math.isfinite(x) or x<=0 for x in p):
        raise ValueError("Invalid price")
    fee=cost_bps/10000
    pnl=[]; baseline=[]; decisions=[]
    prev=0
    for t in range(min_train,len(p)-1):
        # All candidate training outcomes end no later than close[t].
        scores={m:trailing_net(p,m,t,lookback,fee) for m in METHODS}
        candidate=max(METHODS,key=scores.get)
        active=int(scores[candidate]>0 and signal(p,t,candidate)==1)
        actual=p[t+1]/p[t]-1
        realized=active*actual-fee*abs(active-prev)
        pnl.append(realized)
        baseline.append(actual)
        decisions.append({"decision_at":dates[t],"outcome_at":dates[t+1],
                          "model":candidate if scores[candidate]>0 else None,
                          "exposure":"LONG_RESEARCH_ONLY" if active else "ABSTAIN_CASH",
                          "training_score":scores[candidate]})
        prev=active
    if prev: pnl[-1]-=fee
    baseline[0]-=fee
    baseline[-1]-=fee
    latest=len(p)-1
    scores={m:trailing_net(p,m,latest,lookback,fee) for m in METHODS}
    method=max(METHODS,key=scores.get)
    latest_active=scores[method]>0 and signal(p,latest,method)
    out=metrics(pnl)
    buyhold=metrics(baseline)
    exposures=sum(d["exposure"]=="LONG_RESEARCH_ONLY" for d in decisions)
    correct=sum(d["exposure"]=="LONG_RESEARCH_ONLY" and p[min_train+i+1]>p[min_train+i] for i,d in enumerate(decisions))
    return {
        "engine":"FUNDTEX GOD EYE v0.2 - research only",
        "as_of":dates[-1],"observations":len(p),
        "out_of_sample_days":len(pnl),"evaluated_from":dates[min_train],
        "candidate_models":list(METHODS),
        "strategy_net":out,"buy_and_hold_net":buyhold,
        "excess_total_return_vs_buyhold":out["total_return"]-buyhold["total_return"],
        "active_days":exposures,"active_day_positive_outcome_rate":correct/exposures if exposures else None,
        "assumed_one_way_cost_bps":cost_bps,
        "latest_hypothesis":"LONG_RESEARCH_ONLY" if latest_active else "ABSTAIN_CASH",
        "latest_selected_method":method if scores[method]>0 else None,
        "model_selection": "Every day's model selected using only previously observed outcomes; cash if no trailing positive score.",
        "data_quality":"USER_SUPPLIED_UNVERIFIED",
        "assurance":{"independent_live_validation":False,"corporate_actions_checked":False,
                     "point_in_time_universe":False,"licensed_market_data":False,
                     "guaranteed_prediction":False,"broker_execution":False},
        "caveats":["Historical exploratory test, not evidence of predictive alpha.",
                   "Survivorship bias, parameter search, slippage, Indian fees and corporate actions may materially change results.",
                   "Latest hypothesis is not a personalized or regulated investment recommendation."]
    }
