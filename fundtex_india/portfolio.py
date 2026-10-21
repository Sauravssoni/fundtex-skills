"""India cash-equity portfolio analytics: date-aligned, daily-rebalanced hypothetical NAV."""
from __future__ import annotations
import csv
import hashlib
import math
import statistics
from collections import defaultdict
from pathlib import Path
from .market import validate_rows, validate_symbol
from .stats import _percentile, drawdown

def _read_holdings(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or not {"symbol","weight"}.issubset(reader.fieldnames):
            raise ValueError("Holdings CSV must contain symbol and weight columns")
        holdings = []
        seen=set()
        for row in reader:
            symbol=validate_symbol(row["symbol"])
            if symbol in seen: raise ValueError(f"Duplicate holding: {symbol}")
            seen.add(symbol)
            weight=float(row["weight"])
            if not math.isfinite(weight) or not 0 < weight <= 1:
                raise ValueError("Weights must be finite values between 0 and 1")
            holdings.append({"symbol":symbol,"weight":weight,"sector":row.get("sector") or "Unclassified"})
    if not 1 <= len(holdings) <= 30:
        raise ValueError("Portfolio must contain between 1 and 30 positions")
    if abs(sum(x["weight"] for x in holdings)-1)>0.0001:
        raise ValueError("Weights must sum to 1; Fundtex never silently renormalizes")
    return holdings

def evaluate_portfolio(prices_csv, holdings_csv):
    holdings=_read_holdings(holdings_csv)
    bysymbol=defaultdict(list)
    with open(prices_csv, newline="", encoding="utf-8-sig") as fh:
        reader=csv.DictReader(fh)
        if not reader.fieldnames or not {"date","symbol","close"}.issubset(reader.fieldnames):
            raise ValueError("Prices CSV needs date,symbol,close columns")
        for row in reader:
            symbol=validate_symbol(row["symbol"])
            bysymbol[symbol].append(row)
    symbols=[x["symbol"] for x in holdings]
    missing=[s for s in symbols if s not in bysymbol]
    if missing: raise ValueError(f"Missing asset price series: {', '.join(missing)}")
    asset={s:{r["date"]:r["close"] for r in validate_rows(bysymbol[s])} for s in symbols}
    dates=sorted(set.intersection(*(set(asset[s]) for s in symbols)))
    if len(dates)<30:
        raise ValueError("Fewer than 30 common observation dates; cannot fabricate alignment")
    weight={r["symbol"]:r["weight"] for r in holdings}
    sector=defaultdict(float)
    for h in holdings: sector[h["sector"]]+=h["weight"]
    rets={}
    for s in symbols:
        closes=[asset[s][day] for day in dates]
        rets[s]=[b/a-1 for a,b in zip(closes,closes[1:])]
    n=len(dates)-1
    portfolio_rets=[sum(weight[s]*rets[s][t] for s in symbols) for t in range(n)]
    nav=[1.]
    for x in portfolio_rets:
        nav.append(nav[-1]*(1+x))
    means={s:statistics.mean(rets[s]) for s in symbols}
    cov={}
    for s in symbols:
        for t in symbols:
            cov[(s,t)]=sum((x-means[s])*(y-means[t]) for x,y in zip(rets[s],rets[t]))/(n-1)
    variance=sum(weight[s]*weight[t]*cov[(s,t)] for s in symbols for t in symbols)
    variance=max(variance,0.0)
    sigma=math.sqrt(variance)
    rc={s:(weight[s]*sum(weight[t]*cov[(s,t)] for t in symbols)/variance if variance else None) for s in symbols}
    correlations={s:{t:(cov[(s,t)]/math.sqrt(cov[(s,s)]*cov[(t,t)]) if cov[(s,s)]>0 and cov[(t,t)]>0 else None)
                     for t in symbols} for s in symbols}
    q5=_percentile(portfolio_rets,0.05)
    tail=[x for x in portfolio_rets if x<=q5]
    return {
        "product":"Fundtex Financial Intelligence","market":"India","research_only":True,
        "data_quality":"USER_SUPPLIED_UNVERIFIED","prices_sha256":hashlib.sha256(Path(prices_csv).read_bytes()).hexdigest(),
        "holdings_sha256":hashlib.sha256(Path(holdings_csv).read_bytes()).hexdigest(),
        "last_observation":dates[-1],"common_price_dates":len(dates),
        "weights":weight,"sectors":dict(sorted(sector.items())),
        "portfolio_period_return_daily_rebalanced":nav[-1]-1,
        "portfolio_annualized_volatility":sigma*math.sqrt(252),
        "portfolio_max_drawdown":drawdown(nav),
        "portfolio_historical_var95_one_day_return":q5,
        "portfolio_historical_expected_shortfall95_one_day_return":statistics.mean(tail),
        "hhi":sum(x["weight"]**2 for x in holdings),
        "largest_weight":max(x["weight"] for x in holdings),
        "variance_risk_contribution_fraction":rc,
        "daily_return_correlations":correlations,
        "stress_all_assets_minus_10pct":-0.10,
        "data_coverage":{s:{"raw_dates":len(asset[s]),"aligned_dates":len(dates)} for s in symbols},
        "assumptions":["Same-date close-to-close returns only. Missing dates excluded; no forward filling.",
                       "Hypothetical constant target weights, rebalanced daily with zero fees, taxes or slippage.",
                       "Past covariance and VaR are not reliable future-loss bounds; no point-in-time audit.",
                       "No leverage, short sales, derivatives, liquidity/impact modelling, or research advice."]
    }
