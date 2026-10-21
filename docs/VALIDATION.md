# Fundtex Validation Ledger — 21 October 2026

Environment: MacBook Pro, macOS, Python 3.11, isolated QA clone. No broker credentials, production trading or private institutional portfolios accessed.

## Verified local engineering

- **30/30 local Python tests PASSED** including offline NSE UDiFF and historic Google Finance-style importers, source SHA-256 receipts, prequential probabilistic forecasts, no-future-price checks, financial analysis and GOD EYE walk-forward contracts.
- **1,000,000 seeded Gaussian scenario draws PASSED** in **5.22s** in the final full suite. This is CPU computation, not one million actual backtested trades.
- Final temporary-HOME installer verification copied **19 skills into 3 agent skill locations (57 copies)**, then safely skipped all 57 on a second run; the installed evaluation CLI succeeded without any writes into the user's actual home directory.
- Google News source discovery succeeded over HTTPS on one test. RSS headlines are unverified leads. Unofficial Yahoo prices returned HTTP 429 and are not reliable for production.
- Hosted GitHub Actions previously failed before running any steps; CI is not established as green.
- Four third-party historical Indian equity/index archives, ending 2021-01-25: original GOD EYE underperformed buy-and-hold in all four; prequential positive-day-frequency model failed superiority versus an expanding historical-frequency baseline in all four. The research confidence gate ABSTAINED on all four. See EMPIRICAL_RESEARCH.md.
- Exchange licensing, adjustments for dividends/splits, point-in-time universe, signal timing, legal suitability, delistings, slippage, liquidity and real client controls are NOT verified.

## Adversarial six-regime stress evaluation

A separate 2,000,000-path seeded Gaussian computational stress run also PASSED in 8.51 seconds on the test Mac (5-session hypothetical horizon); it is not two million real historical trades.

60 fully synthetic scenarios generated 32,400 price observations and 25,140 prequential forecasts. All 60 correctly withheld prediction approval under a strict baseline-superiority gate; mean Brier skill was -0.4345% versus the expanding-frequency baseline. See [full stress benchmark](STRESS_BENCHMARK.md). This is software robustness evaluation, **not market prediction accuracy**.

## Current predictive classification

**No demonstrated predictive alpha.** Near-80% historical coverage for an 80% return interval does not prove directional skill. Third-party archives are older than five years and have not been independently reconciled to official corporate actions; no claims about today's market follow.

The offline NSE UDiFF importer reads user-provided ZIPs and checks columns, equity series, duplicate dates and ISIN stability. It does not certify exchange authenticity, market data redistribution rights or corporate-action-adjusted returns.

## Institutional go/no-go gates

1. Obtain licensed/authorized NSE/BSE institution-grade prices, revisions, company actions and ISIN master.
2. Add independently verified primary financial disclosures and publication timestamps.
3. Conduct blind, time-causal, multi-asset walk-forward tests against credible baselines with Indian execution charges and impact.
4. Report prospective paper-trial calibration, costs, opportunity-matched benchmark and all failures.
5. Complete SEBI RA/IA, data-licensing and privacy/cybersecurity checks as applicable.
6. Separately verify live website route and hosted CI; a Git commit and a local build do not establish deployment.

**Verdict:** increasingly useful and testable research software, NOT an investment prediction product certified for institutional recommendations. A conservative ABSTAIN is preferable to an unsupported profit claim.

Eleven original US skills copyright Jake Schincariol, MIT. Fundtex India modules developed by Syntheon Technology.
