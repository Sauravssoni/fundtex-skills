---
name: fundtex-india-forecast
description: Forecast-reliability and uncertainty evaluation for sourced Indian NSE/BSE historical equity prices, using leakage-safe prequential probability scoring, Brier baselines, 10/50/90 return intervals, regime tests, empirical calibration, and evidence-based ABSTAIN gates. For a research analyst requesting a forecast audit; never claim guaranteed next-day returns.
argument-hint: "[NSE/BSE equity symbol and authorized historical CSV]"
---

# FUNDTEX FORECAST LAB — INDIA

Authorship: Fundtex Financial Intelligence, Syntheon Technology Private Limited. The CLI is research-only; model confidence is *not* validated with independent live forward data.

## Before estimating anything

Verify symbol/ISIN, company vs benchmark index, venue (.NS/.BO), data source, licensing, as-of IST, corporate action treatment, sample size, date ordering, missing sessions and whether any prior model tuning contaminated the test period. Read actual source or state NOT VERIFIED. Never synthesize a missing quote.

## Reproduce

    fundtex forecast --csv /authorized/INFY-approved-adjusted.csv --symbol INFY.NS --window 252 --margin 0.10
    fundtex evaluate --scenarios 36 --sessions 540 --seed 42

If the terminal is unavailable, explain that the skills file supplies instructions, not executable results, and request runtime support or a JSON result.

## Analyst decision rule

Report: source digest and date, one-session horizon, forecast probability definition, empirical up frequency, 10/50/90 return quantiles, Brier loss vs a fixed 50% predictor and an expanding historical-frequency predictor, central interval nominal/actual coverage, bootstrap uncertainty caveats and whether the provisional gate passes.

The historic 2000–2021 four-instrument India smoke test did NOT demonstrate consistent directional superiority. Even a gate pass in a synthetic evaluation is not independent live calibration. When Brier skill is weak, historical inputs unadjusted, sources stale, sample insufficient, or legal/data permissions uncertain: **ABSTAIN / INVESTIGATE**, not BUY/SELL.

## India-specific safeguards

Observe ex-dividend and split/bonus adjustment, price bands and circuit behavior, missing/no-volume sessions, F&O rollover contamination, company events, macro policy dates and possible ISIN changes. Banks/NBFCs require lender-specific capital/asset-quality metrics; P/E/DCF assumptions must not be transplanted mechanically. NSE and BSE data redistribution rights and firm's SEBI research obligations must be reviewed.

Do NOT present simulated paths, past hit-rates, or quantile interval coverage as certain future direction or performance. No broker orders, secrets or model self-modification.
