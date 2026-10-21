# GOD EYE empirical historical smoke test — 21 October 2026

Data: third-party historical Google Finance / Google Sheets exports from https://github.com/Gajapathy-Selvaraj/Stock_Market_Datasets_NSE. These archival inputs end on **2021-01-25**. Not authenticated against official corporate actions, payouts, delistings, rights, or original as-of data; rights to redistribute not established. Files kept out of the public Fundtex repo.

## Four-way historical policy test

Default GOD EYE research setting: prior-only policy selection, 120 observation warm-up, 60-session history, hypothetical 12 basis points per side, close-to-close execution idealization. These are NOT certified total-return results or investable performance estimates.

| Instrument | Archive span | OOS days | Policy cumulative | Buy-and-hold cumulative | Verdict |
|---|---|---:|---:|---:|---|
| RELIANCE.NS | Jul 2002–Jan 2021 | 4,467 | +234.3% | +3,198.6% | Worse |
| HDFCBANK.NS | Jan 2000–Jan 2021 | 5,090 | +80.8% | +5,693.4% | Worse |
| TCS.NS | Aug 2004–Jan 2021 | 3,929 | +52.7% | +1,800.9% | Worse |
| Nifty 50 index | Jan 2000–Jan 2021 | 4,937 | +223.3% | +876.7% | Worse |

## Prequential probabilistic model

A separate moving 252-session empirical return-distribution model uses only each day's historical prefix. After observing the next close, Fundtex scores Brier loss against both a fixed 50/50 baseline and expanding historical positive-frequency baseline. Central interval coverage nominal 80%.

| Series | OOS days | Brier skill vs 50/50 | Brier skill vs expanding prior | Actual 80% interval coverage | Gate |
|---|---:|---:|---:|---:|---|
| RELIANCE | 4,335 | +0.0014% | -0.0462% | 78.73% | FAIL |
| HDFCBANK | 4,958 | -0.4207% | -0.3523% | 79.16% | FAIL |
| TCS | 3,797 | -0.2321% | -0.2278% | 79.27% | FAIL |
| Nifty 50 | 4,805 | +0.5636% | -0.0444% | 79.71% | FAIL |

**All four abstained** because superiority against independent trivial baselines was not established. Approximate interval coverage does not confer directional predictive skill. Outcomes are historical code-smoke tests on *unverified* archived data, not evidence of accuracy in October 2026.

## What earns institution-grade predictive confidence?

Use an approved point-in-time universe with delistings, accurate corporate actions, timezone-aware publication timestamps, stale/revision controls, real transaction costs and achievable execution. Compare across blind rolling holdouts, sector/market baselines, strong null models, and bull/bear/sideways regimes, with multiple-testing corrections and truly prospective paper trials. Document failures and abstain when confidence is insufficient.

**Current status:** reproducible numerical research tool with no verified alpha. Never market synthetic sample performance or 2000–2021 historical sample as a present-day Indian trading signal.
