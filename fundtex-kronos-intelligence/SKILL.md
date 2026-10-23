---
name: fundtex-kronos-intelligence
description: Run Kronos financial candlestick foundation-model forecasts as an optional offline challenger against naive and momentum baselines on source-verified Indian OHLCV history, with strictly historical walk-forward evaluation and no trades.
---
# FundTex Kronos Intelligence — Predictive Challenger, Not an Oracle

The approved upstream model is **shiyu-coder/Kronos** (https://github.com/shiyu-coder/Kronos), MIT copyright 2025 ShiYu. Verified source `67b630e67f6a18c9e9be918d9b4337c960db1e9a`, October 2026. The underlying paper is `arxiv:2508.02739`; its reported 45-exchange pretraining and financial forecasting benchmarks are source claims, NOT established results on Indian securities or profitable trades.

Supported official weights:
- `NeoQuasar/Kronos-mini` (4.1M, `Kronos-Tokenizer-2k`, 2048 context);
- `NeoQuasar/Kronos-small` (24.7M, `Kronos-Tokenizer-base`, 512 context);
- `NeoQuasar/Kronos-base` (102.3M, `Kronos-Tokenizer-base`, 512 context).

## Autonomous agent routing

When asked to predict, simulate, benchmark or make a cinematic forecast for NSE/BSE, the terminal-capable agent does the workflow:
1. Identify verified ticker and data source, fetch approved actual **open/high/low/close/volume**, exchange-session dates and provenance. If broker access fails, use explicit user-approved historical CSV or date-labelled unofficial OHLC, **not a fabricated real-time feed**. Never use close-only input to invent high/low.
2. Run `fundtex kronos-doctor --size mini` first (no downloads). Inform the user succinctly if the official model and local safetensors are not installed; continue with the baseline study while offering a separately approved model install. Installing the skill does **not** automatically download PyTorch, Kronos code or checkpoints.
3. Run `fundtex kronos-eval --csv /approved/ohlc.csv --symbol INFY.NS --backend persistence --lookback 128 --horizon 5 --origins 12 --stride 5` to establish the independent benchmark. Then, only with locally verified pinned upstream source and safe checkpoint files, run the same command with `--backend kronos --checkout /approved/Kronos --weights /approved/weights/Kronos-mini --tokenizer /approved/weights/Kronos-Tokenizer-2k --size mini --device cpu`. An approved Mac Apple Silicon setup may use `--device mps` after local validation. No model weights are downloaded without user permission.
4. Compare model MAE, RMSE, direction accuracy and performance against persistence and bounded lag drift for identical chronological cutoffs. Explain the strongest negative case, cost/liquidity assumptions, source freshness, adjustments, retraining contamination and confidence. An observed price-model error reduction **does not establish alpha or profitable options spreads**. Never convert probabilistic candlestick simulations into broker-executable returns.
5. For a polished visual, route evidence from genuine OHLC into `fundtex-motion-intelligence`. A forecast video must distinguish history vs simulated future, show invalidation conditions and never show future outcomes at an earlier timestamp. Make no live order, margin, GTT or account changes.

## Model security / precision

`fundtex_india.kronos_runtime` requires the original source from the exact audited SHA, clean git status, official origin and inspected **local `model.safetensors`** checkpoints. No `torch.load` pickle weights, arbitrary `trust_remote_code`, unreviewed forks or silently added external networks. The local inference interface passes *only past observed OHLCV* and separately known **historical session dates**, never future OHLC values. Intraday horizon requires explicit verified exchange timestamps and an independent model/calendar audit; current CLI implements daily historical testing only.

Kronos was pretrained before this FundTex benchmark: its hidden training membership, including NSE/BSE coverage, is unverified. Thus even positive historical scores cannot claim truly unseen pretraining data. Demand forward paper results and repeated independent later sessions before suggesting quantitative advantages. Show `ABSTAIN_UNVALIDATED` when baselines win or data/weights are unavailable.

## Related integrations

- FundTex-Kite approved history → `fundtex kite-mcp-import` into a new source-hashed CSV (login alone is NOT live connectivity)
- `fundtex-strategy-research`: train-only strategy candidates with held-out scoring
- `fundtex-hedged-options`: defined-risk payoff and fee modelling, independent of forecasts
- `fundtex-motion-intelligence`: frame-accurate visual briefing
- `fundtex-connector-orchestrator`: discover actual permitted tool access; never invent broker sessions.

Reference source and third-party licences remain separate from FundTex's new adapter. Research/education only; no promised profit, no orders, and no investment advice.
