# Fundtex validation ledger — 21 October 2026

**Environment:** MacBook Pro, macOS, Python 3.11, clean cloned checkout of this repository inside an isolated QA working directory. No brokerage or production credentials used.

## Confirmed local executions
- First offline run exposed a test-only exact float equality assertion; corrected with approximate float assertion.
- Second full local run (before portfolio extension): **13 tests passed**, 0 skipped, including 1,000,000-path stochastic numerical run. Execution of million draws: **4.81 s** initially and **4.33 s** on post-HTTPS update; different wall timings, same seeded fifth and 95th percentiles.
- Python compileall of all source files: **passed**.
- One-shot installer tested under a *temporary HOME*: first run installed **16 skills** plus isolated CLI engine and launcher; second run skipped all 16 non-destructively; installed launcher returned valid 200-observation synthetic report. The new portfolio skill brings planned total to **17** (run final regression).
- Google News RSS: successful verified-HTTPS retrieval of 3 discovery leads from Mac via OS curl certificate trust fallback. These are unverified headline leads.
- Yahoo chart attempted from Mac: **HTTP 429**. Thus *real-time or delayed Yahoo quote availability is NOT validated*. CSV input path is validated.
- GitHub Actions runs initiated but jobs failed **before execution** (empty job steps; no logs). **Do not call CI green**. Local regression provides the verified result.

## What numerical testing does *not* prove
The test simulates a million random scenario draws from a Gaussian fit to an explicitly synthetic price series. This is **not** 1M historical backtested trades, a trading alpha evaluation, forecast validation, portfolio investment advice, capacity/market-impact testing, or an institution's UAT.

## License & provenance
Source 11 skills authored by Jake Schincariol and retained with his MIT copyright. India additions by Fundtex/Syntheon. No commercial NSE/BSE data licensed.
