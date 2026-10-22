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

## 2026-10-23 quantitative falsification upgrade

If a permitted source supplies only **adjusted closing prices**, never infer next-open returns. For paper research using unofficial public candles, request `fundtex research --symbol VERIFIED.NS --source public-ohlc --period 2y --quote off --out /new/approved/pack`; its raw Yahoo quote OHLC must be explicitly classified `UNOFFICIAL_UNADJUSTED_OHLC_NOT_EXCHANGE_VERIFIED`. A real broker's authorized daily candles are preferred when available. Never mix Yahoo adjusted closes with unadjusted highs/lows; splits/dividends and exchange timestamps still need review. The agent (not the user) builds the strategy rules JSON and runs `strategy-build` with the new pack's `price-history.csv`.

Optional bounded `bootstrap_repetitions: 100..2000` with `bootstrap_seed` enables deterministic moving-block bootstrap on **untouched chronological holdout relative returns**. Treat the interval as a conditional descriptive diagnostic, not a statistical proof of alpha. Always report the three-way ledger: *train-selected excess, held-out excess, and 2x/4x trading-cost stress*. Do not select or modify candidates using the holdout. For more rigorous adversarial analysis the agent can run `fundtex regime-bench --scenarios-per-regime 40 --sessions 540 --seed 42 --cost-bps 15`, which tests a fixed SMA/RSI rule family under *fictional* random-walk, bullish, bearish, mean-reverting and volatility-shock sequences. Five synthetic regimes cannot establish actual Indian strategy performance.

An internal October 2026 demonstration tested three equities using two years of **unofficial, unadjusted** daily candles. Two failed their matched passive holdouts; one showed descriptive outperformance. It is **not evidence of tradable or persistent profitability**, especially with unverified corporate actions, survivorship, Indian charges and asset-selection multiplicity.
