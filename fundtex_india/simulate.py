"""Seeded million-path stochastic scenarios, not historical strategy backtests."""
from __future__ import annotations
import math
import random
import statistics
from .stats import pct_changes, _percentile

def simulate(rows, *, paths=10000, horizon=1, seed=42, position_inr=100000.0):
    if not isinstance(paths, int) or not 100 <= paths <= 2_000_000:
        raise ValueError("paths must be between 100 and 2,000,000")
    if not isinstance(horizon, int) or not 1 <= horizon <= 252:
        raise ValueError("horizon must be 1..252 trading sessions")
    if not math.isfinite(position_inr) or position_inr <= 0:
        raise ValueError("position_inr must be positive, finite")
    if len(rows) < 30:
        raise ValueError("Need 30+ past observations before simulating")
    prices = [float(r["close"]) for r in rows]
    pct_changes(prices)
    logs = [math.log(b/a) for a, b in zip(prices, prices[1:])]
    mu, sigma = statistics.mean(logs), statistics.stdev(logs)
    if not all(map(math.isfinite, (mu, sigma))):
        raise ValueError("Invalid estimated log-return distribution")
    rng = random.Random(seed)
    diffusion = sigma * math.sqrt(horizon)
    drift = mu * horizon
    vals = []
    for _ in range(paths):
        z = rng.gauss(0.0, 1.0)
        ret = math.expm1(drift + diffusion * z)
        vals.append(ret)
    vals.sort()
    q5, q50, q95 = (_percentile(vals, p) for p in (0.05, 0.5, 0.95))
    tail = [x for x in vals if x <= q5]
    return {
        "engine": "independent Gaussian daily log-return / GBM approximation",
        "paths": paths, "horizon_trading_sessions": horizon, "seed": seed,
        "position_inr": position_inr, "sample_observations": len(prices),
        "estimated_daily_log_mean": mu, "estimated_daily_log_stdev": sigma,
        "loss_probability": sum(v < 0 for v in vals) / paths,
        "return_p05": q5, "return_p50": q50, "return_p95": q95,
        "var95_loss_inr": max(0, -q5 * position_inr),
        "expected_shortfall95_loss_inr": max(0, -statistics.mean(tail) * position_inr),
        "stress_minus_10pct_loss_inr": position_inr * 0.10,
        "caveats": [
            "These are simulated distribution draws, not independent historical trades or backtest results.",
            "Gaussian log returns may severely understate crashes, jumps, regime changes and liquidity risk.",
            "Results depend on sample, adjusted-price quality, iid assumptions, seed and forecast horizon.",
            "No model validation, alpha, accuracy or live performance claim is implied."
        ],
    }
