# FundTex Kronos Challenger — verified integration, October 23, 2026
**Research release candidate; never trading/execution.**

## Upstream proof and attribution

- Original project: https://github.com/shiyu-coder/Kronos — **MIT, © 2025 ShiYu**. Reviewed master commit `67b630e67f6a18c9e9be918d9b4337c960db1e9a` (2026-04-13), NOT a community clone/wrapper. Keep original upstream copyright and license with any redistributed upstream code; FundTex does not vendor upstream model.
- Paper: https://arxiv.org/abs/2508.02739 — zero-shot claims across mixed global exchange data; no guarantee of NSE/BSE coverage, independence from pretrained training, pricing alpha, or usable order execution.
- Official local models: `NeoQuasar/Kronos-mini` (4.1M parameters / `Kronos-Tokenizer-2k`, context 2048), `Kronos-small` (24.7M / base tokenizer, context 512), `Kronos-base` (102.3M / base tokenizer, context 512). Large closed.
- Kronos runtime depends on approved PyTorch/safetensors/NumPy/Pandas/einops/HF Hub packages and local model weights. **Installing the FundTex SKILL.md does not install/download this runtime.** Inference is opt-in and local, never an order API.

## First real hardware execution

An authorized Apple Silicon Mac loaded the exact official pinned checkout and real `NeoQuasar/Kronos-mini` plus `NeoQuasar/Kronos-Tokenizer-2k` safetensors in isolated `/tmp` directories. `fundtex kronos-doctor` confirmed all six required optional packages and both checkpoints, correct Git SHA/origin and clean tree. A first real inference failed due to passing Pandas DatetimeIndex rather than Series; that was **fixed after executing the actual upstream predictor**, not concealed by mocks.

First **real model** smoke benchmark (historical *unverified* 495 INFY.NS rows, source SHA256 `5b829f5823ec40936405286c79021ead28f94e421c5302ac83549affff9e5764`; tagged copy sha `677263ddb29dd651a77a97036ac6a3bd40d229573e492f13304ca0a2b0fa06d7`):
- Four chronological forecast cutoffs: 2026-10-08, 2026-10-12, 2026-10-14, 2026-10-16;
- Horizon 2, stride 2, total **8 separately observed close outcomes**; 128 observed candles were permitted per origin. Prediction did not receive future OHLC values.
- Real Kronos-mini `MAE 32.8900`, RMSE `38.6882`, directional accuracy `62.5%`.
- Persistence baseline `MAE 36.5000`, RMSE `42.4869`, direction accuracy `12.5%`.
- Bounded 10-bar drift `MAE 37.1428`, RMSE `40.6391`, direction accuracy `62.5%`.
- Observed MAE improvement vs better simple baseline **+9.89%** in this tiny smoke. There is no statistical validity from 8 outcomes, no calibrated model probabilities, and pretrained training contamination is unknown. Results are descriptive **NOT a signal**.
- No broker session, trade, account information, executable options price or exchange signed receipt was involved. The source was prior unofficial historical OHLC; all market-data rights and corporate actions must be independently verified.

## CLI research sequence

```sh
# These checks read only local code/settings and never download weights
fundtex kronos-doctor --size mini
fundtex kronos-eval --csv /approved/ohlc-with-symbol.csv --symbol INFY.NS \
    --backend persistence --lookback 128 --horizon 5 --origins 12 --stride 5

# Only after explicit approval, installing optional dependencies into a temporary environment,
# pinning the exact upstream source, and downloading official inspected SAFETENSORS locally:
fundtex kronos-eval --csv /approved/ohlc-with-symbol.csv --symbol INFY.NS \
    --backend kronos --checkout /approved/Kronos --weights /approved/Kronos-mini \
    --tokenizer /approved/Kronos-Tokenizer-2k --size mini --device cpu \
    --lookback 128 --horizon 5 --origins 12 --stride 5
```

Output from `kronos-eval` is JSON, including all historical origin dates, observed vs predicted close prices, origin-known direction scores, source hash, model readiness and clearly marked `NOT_VALIDATED_FOR_LIVE_FINANCIAL_SIGNALS`. A hosted ChatGPT skill without a terminal does not automatically run this.

## Mathematical and operational release gates

- Must compare same predeclared cutoffs and data, return-direction anchors relative to **last known origin close** (not future realised closes), no lookahead and no overlapping horizon labels.
- Source **must contain real OHLC**, explicit `.NS/.BO` instrument, chronological dated bars and sensible high-low constraints. Close-only/delayed feeds may not fabricate OHLC; screenshots/style references are not data.
- Benchmark sources and forecast outputs must remain auditable; account portfolios/tokens never in reports.
- Train-time membership cannot be proven unknown for a publicly pretrained model; historical backtests can be **contaminated** even if our implementation obeys causal inference. Demand multiple post-pretraining real forward test periods and asset/regime splits, not 8 retrospective points.
- Stability tests require block/bootstrap uncertainty by cutoff, transaction-cost and slippage sensitivity, corporate action adjustment, sector/index exposure neutralization and registered investment-adviser compliance where applicable. These are **not** solved by a better candle MAE.
- Never use Kronos's predicted OHLC to construct historical derivative chain bid/ask or margin. Options simulation requires actual source-stamped option contract data, expiry assignment/settlement, current lot size and broker-confirmed charges.
- Explore `gxcsoccer/kronos-mlx` on Apple Silicon only after code/security and numerical parity tests; its self-published speed claims are unverified by FundTex.

## FundTex integrations

`fundtex-india-market` + source verification → broker-approved Kite history if genuinely session bound → `fundtex-kronos-intelligence` → challenger/naive evaluation → `fundtex-strategy-research` adversarial research (separate from forecasting) → `fundtex-motion-intelligence` evidence-linked scene, forecast separate from observed → analyst report with strong bear case, invalidation conditions and ABSTAIN when edge cannot be substantiated.

Nothing here deploys a multiuser broker gateway or modifies the personal Zerodha connection. FundTex gateway security changes remain in separate private review PRs.

## Expanded real model falsification (completed)

On the same unverified 495-bar INFY.NS source and model checkpoints, Kronos-mini was evaluated on a **larger, predeclared 12-cutoff / 5-session horizon** (60 forecasted close outcomes, stride 5, past 128 bars), using Apple-Silicon MPS acceleration. Model weights actually loaded once; elapsed wall runtime **172.72 seconds**. Results from source-hashed private local JSON:
| Scorer | MAE (price points, ₹) | RMSE | Direction vs origin close |
|:--|--:|--:|--:|
| Kronos-mini | 39.1168 | 50.4351 | 60.0% |
| Persistence | **35.4550** | **46.8240** | 43.3% |
| Bounded 10-bar drift | 40.0094 | 50.8275 | 45.0% |

**Major falsification:** Kronos **underperforms simple persistence on absolute error by 10.33%** despite better directional accuracy in this tiny, correlated sample. It is **not permitted to become the default FundTex price forecaster or automatically trade**. The first 8-outcome 9.89% gain was an unstable smoke-test artefact, not a validated edge. Reporting both tests is mandatory.

### Independent long-or-cash paper test (not model retraining)

`fundtex kronos-paper` consumes the immutable original benchmark JSON and original exact source SHA. It separately simulates **12 non-overlapping historical hypothetical windows**, signal made at the model's original prior close, next OPEN as an optimistic fill and horizon exit at observed closing price. A forecast direction above the origin close produces LONG exposure, otherwise flat CASH. No shorting, leverage, trading/broker calls, portfolio access or F&O positions. Threshold fixed at zero; no post-test optimization.

On this retrospectively observed and **unverified** sample Kronos signalled LONG in 7 of 12 windows. Under arbitrarily chosen **20 bps total round-trip cost** (NOT verified actual Indian costs), the arithmetic strategy path compounded to **+14.58%** over the 12 selected windows, versus +2.95% always-long on every sampled window. At hypothetical 0 bps: +16.17% versus +5.44%; at 50 bps: +12.24% versus −0.69%. These are **non-executable hindsight paper figures** and must not be advertised as achieved portfolio returns: optimistic fills, arbitrary friction, small sample, equal-notional assumptions, noncontinuous window selection, possible model pretraining leakage.

Shuffling the same number of signals across the 12 windows for 2,000 seeded placebo permutations yielded a gross figure at least as large in **6.95%** of permutations. This does **not** establish predictive statistical significance, particularly with autocorrelated prices and known model-pretraining overlap uncertainty.

**Decision gate: FAIL / unvalidated alpha.** Robust cross-sectional and later-dated tests with transaction logs, bid/ask, pricing sources and licensed market data must precede any trading claims. Price MAE, price direction and paper P&L answer *different questions* and must remain separate.

Commands: `fundtex kronos-eval` generates the audit report; `fundtex kronos-paper --report /approved/eval.json --csv /approved/exact.csv --symbol INFY.NS --permutations 2000` runs the source-matched falsifier. Both are read-only.
