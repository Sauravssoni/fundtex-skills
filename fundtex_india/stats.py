"""Deterministic, auditable daily-close statistics (not predictive recommendations)."""
from __future__ import annotations
import math
import statistics

def pct_changes(closes):
    if len(closes) < 2 or any(not math.isfinite(x) or x <= 0 for x in closes):
        raise ValueError("Need at least 2 strictly positive, finite closes")
    return [b / a - 1 for a, b in zip(closes, closes[1:])]

def drawdown(closes):
    peak, worst = closes[0], 0.0
    for price in closes:
        peak = max(peak, price)
        worst = min(worst, price / peak - 1)
    return worst

def _percentile(xs, p):
    if not xs:
        raise ValueError("Empty return series")
    s = sorted(xs)
    k = (len(s) - 1) * p
    low = int(k)
    return s[low] + (s[min(low + 1, len(s)-1)] - s[low]) * (k - low)

def _rsi(closes, window=14):
    if len(closes) <= window:
        return None
    diffs = [b - a for a, b in zip(closes, closes[1:])][-window:]
    gain = sum(max(x, 0) for x in diffs) / window
    loss = sum(max(-x, 0) for x in diffs) / window
    if loss == 0:
        return 100.0 if gain else 50.0
    return 100.0 - 100.0 / (1.0 + gain / loss)

def report(rows, *, annual_risk_free=0.06):
    if len(rows) < 30:
        raise ValueError("At least 30 observations needed for basic risk metrics")
    if not 0 <= annual_risk_free < 1:
        raise ValueError("Risk-free rate must be a decimal between 0 and 1")
    prices = [float(x["close"]) for x in rows]
    changes = pct_changes(prices)
    mu = statistics.mean(changes)
    sigma = statistics.stdev(changes)
    q5 = _percentile(changes, 0.05)
    tail = [r for r in changes if r <= q5]
    annual = 252
    return {
        "first_date": rows[0]["date"], "last_date": rows[-1]["date"],
        "observations": len(prices), "last_close": prices[-1],
        "period_return": prices[-1] / prices[0] - 1,
        "mean_daily_return": mu, "daily_volatility": sigma,
        "annualized_volatility": sigma * math.sqrt(annual),
        "annualized_sharpe_approx": ((mu * annual) - annual_risk_free) / (sigma * math.sqrt(annual)) if sigma else None,
        "maximum_drawdown": drawdown(prices),
        "historical_var95_one_day_return": q5,
        "historical_expected_shortfall95_one_day_return": statistics.mean(tail),
        "sma20": statistics.mean(prices[-20:]) if len(prices) >= 20 else None,
        "sma50": statistics.mean(prices[-50:]) if len(prices) >= 50 else None,
        "sma200": statistics.mean(prices[-200:]) if len(prices) >= 200 else None,
        "rsi14": _rsi(prices),
        "methodology": "Daily close-to-close arithmetic returns; 252-session convention; historical 5% left tail; sample Sharpe.",
        "caveats": ["Historical risk is not a future-loss limit.",
                    "Corporate actions and adjusted closes depend on imported data quality.",
                    "Do not infer next-day direction from technical indicators."]
    }
