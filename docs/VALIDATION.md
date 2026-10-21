# Fundtex Validation Ledger — 21 October 2026

Environment: MacBook Pro, macOS, Python 3.11, isolated QA clone. No broker credentials, production trading or private institutional portfolios accessed.

## Verified local engineering

- **26/26 local Python tests PASSED** including offline NSE UDiFF and historic Google Finance-style importers, source SHA-256 receipts, prequential probabilistic forecasts, no-future-price checks, financial analysis and GOD EYE walk-forward contracts.
- **1,000,000 seeded Gaussian scenario draws PASSED** in **4.32s** in the latest full suite. This is CPU computation, not one million actual backtested trades.
- Prior temporary-HOME installer run copied **18 skills into 3 agent skill locations (54 copies)**, then skipped all 54 on a safe second run; installed command-line analyzer worked. Changes to installer after that require another audit.
- Google News source discovery succeeded over HTTPS on one test. RSS headlines are unverified leads. Unofficial Yahoo prices returned HTTP 429 and are not reliable for production.
- Hosted GitHub Actions previously failed before running any steps; CI is not established as green.
- Four third-party historical Indian equity/index archives, ending 2021-01-25: original GOD EYE underperformed buy-and-hold in all four; prequential positive-day-frequency model failed superiority versus an expanding historical-frequency baseline in all four. The research confidence gate ABSTAINED on all four. See EMPIRICAL_RESEARCH.md.
- Exchange licensing, adjustments for dividends/splits, point-in-time universe, signal timing, legal suitability, delistings, slippage, liquidity and real client controls are NOT verified.

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
