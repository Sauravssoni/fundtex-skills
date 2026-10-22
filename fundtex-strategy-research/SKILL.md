---
name: fundtex-strategy-research
description: Convert ordinary-language trading hypotheses into constrained RSI or moving-average research strategies, run next-open historical backtests on genuine OHLC, compare train-only parameter search with untouched holdout and stressed costs, then challenge predictive claims.
---

# Fundtex Strategy Research | Research first, execution disabled

**Natural-language strategy → safe bounded JSON rules → reproducible experiment.** An authorized agent identifies symbol/ISIN and user-approved OHLC history, checks timestamp/split adjustment and file provenance, then creates a locally approved small JSON config with `candidates` of `{"name":"sma_cross","fast":10,"slow":50}` or `{"name":"rsi_reversion","entry":30,"exit":70}`. Supply `split_fraction` typically 0.7 and `cost_bps_per_position_change` from actual broker assumptions; do not silently treat a 15-bps example as a complete India STT/fees schedule.

Invoke via terminal (agent handles the command):

`fundtex strategy-build --csv /approved/actual-OHLC.csv --symbol INFY.NS --inputs /approved/strategy-research.json`

The tool refuses close-only data (never fabricate an open), imposes minimum history and limited parameter candidates, derives signals from completed closes, enters no earlier than the following real bar open and measures open-to-open returns. It selects candidate parameters using **training data only**, evaluates on separate untouched chronological holdout, compares matching buy-and-hold, and performs 2x/4x assumed friction stress. It does not permit arbitrary Python strategies, unbounded optimization, short exposure, leveraged orders or trade execution.

Every packet must disclose trade count, selection bias, holdout dates, source SHA, worst drawdown, realistic STT/GST/brokerage/stamp/impact caveat, end-of-sample exposure and contrary benchmarks. The present engine is an exploratory close-signal equities research evaluator, **not** a broker options-chain backtester. Real F&O strategy testing needs historical instrument-level options chains, greeks, lot revisions, IV/skew, expiries, corporate actions and exchange-approved settlement costs before claiming statistical performance.

A strategy that wins on one historical holdout is not validated alpha. Multiple time/asset-regime independent validation, uncertainty intervals, shadow paper trading and peer review are required before any investment decision. `ABSTAIN` where evidence is missing.
