# FundTex Million-Path & Strategy Robustness Audit — 23 October 2026

**Status:** reproducible engineering research preview. **No authenticated NSE/BSE quote, orders, licensed feed, audited financial statement, registered advice or proven trading alpha.** All numerical option premiums are deliberately fictional.

## 1. Verified real execution environment and source scopes

Runs executed on a paired, permissioned Apple Silicon MacBook Pro (M1 Pro) in an isolated temporary checkout of `feature/million-path-strategy-validation-20261023`. Python 3.11.6 with a constrained environment, no broker environment credentials. The computer performed actual processes; no cloud-simulation claims.

**Historical price data:** the public `yahoo_ohlcv_prices` adapter obtained raw unadjusted daily quote OHLC for `INFY.NS`, `RELIANCE.NS` and `ICICIBANK.NS` for 2-year requests. The outputs were marked `UNOFFICIAL_UNADJUSTED_OHLC_NOT_EXCHANGE_VERIFIED`, last observation **2026-10-21**, and the 495-row strategy inputs were re-read from generated pack CSVs. The backtest import properly classifies re-imported local records `USER_SUPPLIED_UNVERIFIED`; no transitive exchange-vendor license or audit is implied. Corporate actions, adjusted vs unadjusted splits and timestamps need primary reconciliation.

## 2. Million-path simulations and engineering performance

| Gate | Input/data | Replications | Duration | Observed |
| --- | --- | ---: | ---: | --- |
| Existing return-distribution simulation | Fictional `examples/india_prices.csv`, RELIANCE.NS-labelled fixture | **1,000,000** | 4.68 seconds (first run); 4.80 seconds (independent repeat) | p05 daily return −0.010905, p95 +0.012979, all assertions PASS |
| Hedged-options terminal payoff | Fictional NIFTY 25,000 spot, 75 example lot, short 25,000 put @150, long 24,800 put @90 | **1,000,000** | 25.32 seconds (first concurrent run), **12.40 seconds** (explicit repeat) | Mean −₹2,005.25; positive frequency 54.6129%; model max loss ₹10,571.85; PASS |
| Volatility parameter grid | Same fictional options; 5 separate volatility assumptions; 200k paths each | **1,000,000 total** | 13.06 seconds | Volatility-dependent mean losses; all simulations succeeded |
| Strategy regimen | Five intentionally artificial market generators × 40 histories each | 200 historical-path scenarios, **600 candidate-fit evaluations** | 19.04 seconds | Time-separated holdouts, no strategy trading authority |

**Total explicit million-scale stochastic option/return draws across the three distinct campaigns: 3,000,000.** Repeat executions are reproducibility checks, not independent evidence of profitability. A "path" is one RNG realization under the assumed generator, not one trading day or separate historical trade.

The modeled one-million-path positive-P&L frequency 95% Wilson **sampling** interval was [54.5153%, 54.7105%]; modeled mean P&L **sampling** interval [−₹2,019.18, −₹1,991.32]. These bounds assume the terminal-lognormal model and its original premiums, rates, volatility and omitted costs. They **do not include model, source, liquidity or settlement uncertainty**.

### Five-volatility stress of the same fictional put-credit vertical

| Assumed annual volatility | Draws | Positive payoff fraction | Mean entry-fee-adjusted modeled P&L |
| ---: | ---: | ---: | ---: |
| 10% | 200,000 | 60.1680% | −₹858.33 |
| 15% | 200,000 | 56.6295% | −₹1,587.47 |
| 20% | 200,000 | 54.7885% | −₹1,977.70 |
| 30% | 200,000 | 52.8240% | −₹2,396.74 |
| 40% | 200,000 | 51.7175% | −₹2,627.43 |

Even above-50% positive payoff frequencies coincide with **negative means**. Do not market this fictional structure as an attractive position.

## 3. Adversarial five-regime strategy campaign (fully artificial prices)

Candidates were declared before seeing outcomes: SMA(10/50), SMA(20/80), RSI(30/70); next-open fills on generated actual OHLC candles; one 70/30 chronological selection/holdout split per synthetic history; 15 bps per position change cost assumption (not a complete Indian tax ledger).

| Artificial generator | Independent histories | Outperformed matched passive holdout | Mean holdout net excess return |
| --- | ---: | ---: | ---: |
| Independent random walk | 40 | 47.5% | +0.4575 percentage points |
| Upward drift | 40 | 17.5% | −5.6578 percentage points |
| Downward drift | 40 | 55.0% | +3.2595 percentage points |
| Log-price mean reversion | 40 | 47.5% | +1.4714 percentage points |
| Volatility regime shock | 40 | 50.0% | +3.9033 percentage points |

Most worrying modeled strategy drawdowns by generator: random walk −27.7%, upward drift −19.0%, downward drift −36.6%, mean reversion −12.6%, and volatility shock **−60.3%**. Synthetic results alone cannot measure real strategy win rates or skill.

## 4. Three real-source dated historical exploratory strategy tests

Same three predeclared rules and 15-bps assumed per-change friction. 495 input OHLC observations per company, 148 holdout sessions; 2-year Yahoo public raw unadjusted quote provenance, 2026-10-21 last observation. Data and corporate actions independently unverified.

| Ticker | Training-only selected rule | Holdout strategy return | Holdout passive return | Absolute excess | Result |
| --- | --- | ---: | ---: | ---: | --- |
| INFY.NS | SMA 10/50 | −12.4112% | −7.6859% | −4.7254 percentage points | `NO_OBSERVED_NET_EXCESS` |
| RELIANCE.NS | RSI 30/70 | −12.6353% | −12.5036% | −0.1317 percentage points | `NO_OBSERVED_NET_EXCESS` |
| ICICIBANK.NS | RSI 30/70 | +17.6326% | +12.3093% | +5.3233 percentage points | `DESCRIPTIVE_NET_OUTPERFORMANCE_NOT_PROVEN_ALPHA` |

The ICICI result is **not proven alpha**. With opt-in 1,000-replicate moving-block bootstrap, the **relative terminal wealth ratio minus one** was +4.7399% and its exploratory 95% interval was **[−8.9338%, +22.1791%]**, crossing zero. The relative-ratio figure is not the absolute percentage-point difference in returns. The bootstrap is a descriptive resampling of this one holdout, not a multiple-testing-adjusted independent alpha test.

Baseline buy-and-hold is computed without its own trade-entry costs, so the strategy comparison is conservative but not a complete apples-to-apples trade ledger. Dividend income, rights, delisting and survivorship, futures basis and option contract revisions, 2026 India fee schedules, spread/liquidity, data license and broker margin are unresolved.

## 5. Bugs caught and fixes implemented

1. **Phantom-candle data pipeline:** the historic report CSV can contain open/high/low headers with blank values for close-only series. The studio parser now classifies fully blank OHLC columns as close-only and rejects partially or mixed populated rows. The backtester rejects anything without genuine opening prices. Added round-trip tests.
2. **Adjusted-close contamination:** default public `yahoo_prices` uses adjusted close for line research but must not manufacture OHLC by combining adjusted closes with unadjusted opens/highs/lows. A **separate `public-ohlc` source** reads provider-supplied raw open/high/low/close only, validates full-bar geometry and ticker identity, rejects bad bars and omits incomplete ones with a count. Unadjusted status is explicit. Added mocked provider regression tests and real provider smoke runs.
3. **Uncertainty overclaim risk:** added conditional Monte Carlo 95% sampling intervals and an opt-in moving-block bootstrap with explicit `not_a_significance_test_or_calibrated_alpha` flag. No auto order route or direct broker authorization added.
4. **Regime dependence:** new deterministic `fundtex regime-bench` adversarial harness highlights downtrend vs uptrend asymmetric performance and worst drawdown; its only inputs are synthetic generators.

## 6. Strict release determination

Keep experimental source in **draft feature branch**, do not merge to production or publish performance claims. Before real options margin/signal use, obtain an authorized broker market-data connection with instrument master, exact lot expiry, corporate actions, option chain/tick data, historical IV skew, settlement/assignment, licensed rights and date-scoped tax/fee tables. Validate against a professionally audited event-driven options backtester, including untouched out-of-market testing and blind paper trading. No strategy auto-execution in FundTex research engine.

Commands supported by real CLI agent:
```bash
RUN_MILLION_TEST=1 python3 -m unittest -v tests.test_fundtex_million
fundtex regime-bench --scenarios-per-regime 40 --sessions 540 --seed 42 --cost-bps 15
fundtex research --symbol INFY.NS --source public-ohlc --period 2y --quote off --out /new/approved/pack
fundtex strategy-build --csv /approved/pack/price-history.csv --symbol INFY.NS --inputs /approved/strategy.json
```
Normal end users should describe the research task in natural language to a genuinely terminal-enabled, installed coding agent; it executes these commands and validates output. No syntax memorization is part of the end-user UX.
