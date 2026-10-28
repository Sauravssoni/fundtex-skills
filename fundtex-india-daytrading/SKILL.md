---
name: fundtex-india-daytrading
description: India-first agent-native, paper-only intraday scanner and opening-range breakout analysis, next-bar research entry, risk-sized stop and target, prior-session Time Machine replays, event/news challenges and chart-film research; no orders.
---
# FundTex Indian Day Trading Intelligence — safer than a viral skill demo

**User intent:** "Find Nifty/NSE/BSE setups", "monitor the opening range", "is this intraday entry worth the risk?", "simulate 10k or 1m paths", "time machine", "risk and budget", "chart to video", "teach me". Agent handles validated inputs and outputs; never force a new user to hand-write JSON or run commands. Broker login is one consent-gated read-only process when actually supported.

### Attribution and research baseline

Inspired by, but NOT a blind copy of, Jake Schincariol's MIT-licensed `Jakeschincariol/day-trader-skill` (https://github.com/Jakeschincariol/day-trader-skill ; © 2026 Jake Schincariol). Its 11 US-focused skills include scanner, news, entry, exit, Time Machine, risk, budget, broker, alerts, analyst and congressional disclosure tracker. FundTex's original India-focused implementation implements/coordinates equivalent research stages but does NOT install US Alpaca broker execution, NYSE 9:30–16:00 calendars, US FINRA day-trading/tax rules, or speculative Congress trade signals.

### Default autonomous run (no real orders)

1. **Verify source.** Discover broker data tools in this host. Ask for Zerodha official login once only when needed and user-approved; a ChatGPT plugin being "connected" is NOT broker authentication. If official Kite MCP fails session binding, continue with a user-authorized, dated broker export or clearly labelled unofficial historical data. Do not infer tick prices, volume, highs/lows or time from screenshots.
2. **Verify NSE/BSE equity identity and session.** Default is Indian cash equities, trading hours usually 09:15–15:30 **IST** on confirmed full trading days. Respect official exchange holiday/special-session calendar as an independent source; current engine declines incomplete/irregular days and flags holiday verification missing. For actual futures/options, use dedicated `fundtex-hedged-options` with contract expiry, lot, point-in-time bid/ask and actual fees; DO NOT run the equity ORB paper model on options.
3. **Research scanner and setup.** Load **completed** 5-minute OHLCV bars with timezone offsets, full-session grid and 20 or more PRIOR sessions. Build 15-minute opening range (3 bars; configurable 1–6). A wick beyond resistance does not trigger; require the first close beyond the confirmed high. No same-candle fill or future observations.
4. **Entry/exit plan.** Historical paper entry is the NEXT candle's open, not the breakout bar's close. Set initial stop at opening-range low and illustrative 2R target. Verify the geometry and explain gaps, volatility, possible order-book slippage and news risk.
5. **Risk and capital.** Require explicitly approved INR risk budget and quantity. Run trade-risk constraints; show PASS/BLOCK as a **paper** verdict only. Include per-side fees and slippage assumptions, but warn that cost rates are placeholders, stop fills are not guaranteed and the simulation doesn't calculate live leverage/margin or exact STT, stamp duty and GST.
6. **Time Machine simulation.** Use only historical fully observed sessions strictly before the historical plan date, resampling slot-conditioned relative 5-minute bars with bounded random jitter. Seed deterministically; 10,000 paths default, configurable up to 1,000,000 for isolated benchmark workloads. Model "both sides touched" as stop-first, gap-through as worse-than-stop. Report P(loss), P(net positive), expected P&L, median, p05, p95 and worst simulated. This distribution is **conditional resampling**, not true forward odds or a guarantee. Bootstrap and out-of-time paper follow-ups are needed before a predictive claim.
7. **Challenge it.** Verify dated BSE/NSE corporate announcements, news, RBI/sector effects and volumes with source citations. Include false breakouts, costs, news gaps, stale source and negative cases. No US Pelosi disclosures/SEC EDGAR should be presented as Indian trading signals. `fundtex-kronos-intelligence` may join as an independent **challenger**, never auto-approved as predictive alpha (earlier India test failed a naive baseline on MAE).
8. **Communicate and learn.** Write source-labelled structured JSON, ask the existing FundTex chart and motion skills to render observations versus simulated futures distinctly, explain 2R, next-bar fills, and the risk that simulation misses rare jumps. Default output is a research brief and educational paper plan. Alerts should be opt-in, read-only and respect broker/source polling limits; NEVER pretend an agent continues monitoring when no real scheduler is running.

### Agent-native command

After obtaining a permitted **complete** dated 5-minute CSV with schema `timestamp,symbol,open,high,low,close,volume` and a real source label, execute in an authorized local terminal:

```bash
fundtex india-daytrade --csv /approved/intraday_5m.csv --symbol INFY.NS \
  --session-date YYYY-MM-DD --as-of-slot 75 --or-bars 3 \
  --quantity 1 --risk-budget 1000 --paths 10000 --seed 19
```

The engine returns `plan` and `replay` (or no trade when the setup is missing), with `orders_enabled:false`, `real_trades:0` and source hash. **If user asks for a million-path stress test** the agent may run `--paths 1000000` in an authorized environment within the compute budget; never claim a million runs from a 10k output. No web plugin skill runs Python by itself without a terminal/tool adapter.

### 11 upstream feature ideas mapped to FundTex

| Original US capability | FundTex-native implementation / limitation |
|---|---|
| Scanner | Indian cash-market completed-bar ORB, optional candidate universe with verified data |
| News monitor | Primary NSE/BSE filings and independent source/timestamp checks |
| Entry timer | Completed 5m bar, next-bar paper execution; no self-running watcher |
| Exit planner | Stop, target and historical gap-aware paper P&L |
| Time Machine | Prior-session-only 10k–1m resampled paths, no forecast promises |
| Risk manager | INR paper risk-budget PASS/BLOCK, no broker account calls |
| Budget manager | Position-size math under known equity cash budget, separate regulated derivatives |
| Broker | User-consented read-only data; **NO order connector** |
| Alerts | Source/permission-aware plans; actual delivery requires a connected monitoring service |
| Analyst | FundTex primary filings, valuation, and negative-case council |
| Pelosi / Congress | US-specific, **not silently imported** into India analysis; optional US research only with source/regime qualifications |

### Current release gates

- No promise of precise live data from Yahoo; current Zerodha web MCP broker session was shown to fail after successful browser login. Restrict product quote badges until actual provider tools respond.
- No implicit investment advice, no automatic trades, no brokerage order ticket, no portfolio/account ingestion.
- No Indian tax/cost compliance claim from placeholder fee rates. Cash equities only.
- No inference of OHLC/volume from an image or a close-only feed.
- True NIFTY F&O options require the separate contract-aware payoff engine and broker-verified lot/margin/settlement.
- Preserve upstream MIT attribution; the FundTex engine is independent code and no upstream python modules are silently copied.
