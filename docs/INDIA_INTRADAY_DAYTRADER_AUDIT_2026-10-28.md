# FundTex India Intraday Desk — independent integration QA
**Prepared 28 October 2026. Research only. No live brokerage orders.**

## Reference implementation audited

- Source: https://github.com/Jakeschincariol/day-trader-skill
- Author: **Jake Schincariol**, MIT copyright 2026; commit observed `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` at 28 Oct 2026. Original GitHub README describes **11** Claude day-trading skills.
- A clean isolated public source clone was audited on the authorized Mac. Its offline Python test suite reported **315 tests, all passed** (source-local suite, 399.635 sec). This proves its fixtures/tests pass in that environment, **not trading profitability or security of hosted broker connectors**.
- Do not copy blindly: it is designed around **US** symbols, Nasdaq Trader universe, NYSE ET hours and the Alpaca brokerage. Its "Time Machine" is historical bar resampling, **not all possible futures or a guaranteed probability of execution**.
- Our new `fundtex_india/intraday_desk.py` is an independently authored India-aware cash-equities implementation, not an unreviewed package install or any redistribution of the author's scripts. Preserve upstream author attribution and MIT terms if later vendoring substantial code.

## Functional benchmark mapping

| Original role | FundTex India integration | Implementation status |
|---|---|---|
| Scanner | `fundtex india-scan` explicitly approved directory of NSE/BSE 5m OHLCV; full-session grid, rejects invalid feeds and discloses failed instruments | Implemented for **offline historical input**, not thousands of verified live stocks |
| News | Existing primary exchange/SEBI filings and FundTex news agent; negative event checks | Available as separate research skills; not yet a verified live streaming event feed |
| Entry | Full 09:15–15:30 IST 5min completed-bar ORB: first **close** above 15m high; next candle OPEN paper entry | Implemented; no feed latency proof |
| Exit | Range-low stop, illustrative 2R target, stop-first if both stop/target touched, **gap-through worsens loss** | Implemented as paper geometry |
| Time Machine | 20+ **prior** full sessions; relative-bar slot resampling with jitter, deterministic seed, 10k default, up to 1m accelerated paths | Implemented; simulated outcomes only |
| Risk | INR paper risk budget, estimated assumed fees/slippage; BLOCK trade candidates violating risk | Implemented but NOT full Indian tax or brokerage margin engine |
| Budget | Explicit whole-share quantity; no borrowed leverage or short-selling | Partial paper sizing; not broker purchasing-power verification |
| Broker | Optional authorized *read-only* quote and candle tools; zero orders exposed by this module | Brokerage gateway separate and **not deployed** |
| Alerts | Agent may advise explicit monitoring only if a real connected scheduler exists | No background alerts are pretended |
| Analyst | FundTex fundamental, council/Kronos challenger and chart/video engine | Existing separate workflows, no live validation of predicted alpha |
| Pelosi | US congressional disclosure workflow | Deliberately **not imported as an India market signal** |

## Verified release gates (synthetic market fixtures only)

1. Reconstructed exactly 31 synthetic complete weekday NSE-style sessions with **75 five-minute candles per day** and explicit +05:30 timezone, and a known ORB trigger at slot 3.
2. Eight isolated tests passed: immutable causal cutoff, same-bar entry prevention, conservative gap/dual-trigger, paper risk block, invalid candle rejection, determinism/bounds, multi-symbol scanner and both CLI command outputs. No real trading.
3. Original scalar 10k-path benchmark consumed ~30.0s on authorized Mac. Streaming early-exit optimization reduced it to ~11.35s (different deterministic PRNG draw sequence, therefore not identical resulting outcomes).
4. NumPy PCG64 optional batch engine is gated at **≥50,000** paths and operates in bounded 8192-path chunks. Verified **50,000 paths**, no missing outcomes, ~12.27s on Mac. Supports up to 1m; independent 1m benchmark must be recorded before claiming executed million simulations.
5. Risk result sources explicitly say historical resampling is **not forward probability**. Simulated stop prices are not loss guarantees; gap losses can exceed stop. Assumed fee/slippage rate is intentionally not certified as current official NSE charges.
6. Each report includes exact source SHA256, source-quality label, completed-bar timestamp, scenario count, seed, numerical P&L distribution, no-orders flags and explicit official-exchange-calendar limitation.

## Safe reproducibility

```bash
# Full but OFFLINE single historical instrument from explicitly approved, complete 5m csv
fundtex india-daytrade --csv /approved/INFY.NS.csv --symbol INFY.NS \
  --session-date 2026-10-23 --as-of-slot 75 --or-bars 3 \
  --quantity 1 --risk-budget 1000 --paths 10000 --seed 19

# Historical multi-file discovery from specifically approved source folder
fundtex india-scan --folder /approved/nse-fiveminute-csvs --session-date 2026-10-23 \
  --as-of-slot 75 --or-bars 3 --max-files 250

# Isolated numerical stress only if host supports NumPy and compute budget
fundtex india-daytrade ... --paths 1000000
```

CSV schema `timestamp,symbol,open,high,low,close,volume`, timestamp is **completed 5-minute candle START** with ISO8601 timezone offset. Only full 75-bar regular sessions accepted. For current-day research the present evaluator uses full sessions; do not claim an active mid-session live scanner until partial-day feed support and official calendar are developed.

## Important limitations / next tasks

- Require a verified, licensed intraday NSE/BSE data feed and exchange holiday/special-session calendar. This module will *not* manufacture historical opening prices from a chart image or close-only quotes.
- Real intraday alerts require a consented scheduler and anti-spam controls; CLI invocation is neither autonomous scheduling nor always-on streaming.
- Official India exchange fees, stamp duty, STT, GST, broker margins, corporate actions, option delivery rules and expiry contract details must be separately validated. Current fixed per-side fee and slippage rates are **explicit illustrative parameters**.
- Opening-range/target-replay P&L is hypothetical. Need out-of-time data, loss-tail calibration, bootstrap intervals, benchmark vs no-trade, taxes and adverse event stress; a million **simulated** paths do not turn it into a proven strategy.
- Strictly separate this **cash equity long-only research engine** from FundTex's derivatives hedging/option-chain simulation. Do not route contract-specific options payoffs through a simple stop-loss backtester.
- Production web broker integration remains blocked on user-scoped OAuth and a server-enforced read-only gateway. Existing direct Zerodha MCP test showed browser login success but quote/session binding failure. No broker account read or trading call was used in this run.
- Private ChatGPT plugin source includes the specialist skill; a skills-only plugin cannot automatically run local Python or trade without an authorized executor. Do not claim installed release updated until Plugin Creator confirms.

## Current development branches

- Public source: `feature/india-daytrading-guarded-desk-20261028`
- Private package: `feature/fundtex-plugin-v011-daytrade-20261028`
- Production `main` unchanged pending proof and review.
