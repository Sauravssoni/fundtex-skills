---
name: fundtex-fusion-desk
description: Run one unified India-first analyst desk combining primary evidence, World Monitor geopolitical context, dated charts, conservative intraday replay, source-checked Kronos benchmark, risk/cost review and financial video.
---
# FundTex Fusion Desk — One Evidence Plane

This is FundTex's **original** analyst/terminal orchestration—not a Fincept clone or redistributed World Monitor app. An external source is a **provider**, not a license to copy AGPL application code. No trade orders, credentials or exchange redistribution.

**First user request:** Automatically detect existing host research/terminal/MCP tools, reuse approved context, choose a valid instrument and source. Don't require users to learn separate terminal commands. If the host offers FundTex/WorldMonitor MCP, confirm real tool availability, user's OAuth consent, provider attribution and observed time; never claim live access because a plugin card exists. If absent, run signed/dated offline evidence and explain missing live inputs.

**Normal analysis sequence**
1. Identity: actual `.NS`/`.BO` symbol, ISIN, India time and market holiday/expiry constraints
2. Evidence: primary NSE/BSE/RBI/SEBI/company disclosures; optionally official World Monitor `get_sources`, `get_world_brief`, `get_country_risk`, `get_market_data`, `get_news_intelligence`, `get_chokepoint_status` through **user-authorized** hosted MCP. Never substitute global intelligence for exchange-confirmed prices.
3. Import only approved event JSON with explicit `source`, `published_at`, `observed_at`, category and symbolic links. Run `fundtex fusion-desk --events /approved/events.json --as-of 2026-10-28T03:30:00+05:30 --symbol INFY.NS`. Source receipts and duplicate detection are strict; current as-of must be actual, not copied from an example.
4. For actual **75 complete NSE/BSE 5m candles/session**, use `--intraday /approved/5m.csv --paths 10000` for paper-only opening-range breakout replay. Missing bars exclude a session; 10,000 bootstrap resamples are conditional on historical observations, not a profitable strategy guarantee. No live order book, actual stops or derivative margin.
5. Route to existing `fundtex-god-eye` for primary-file forensic work, `fundtex-kronos-intelligence` for optional challengers, `fundtex-strategy-research` for holdout backtests, `fundtex-hedged-options` for independently sourced derivative payoff and `fundtex-motion-intelligence` for historical charts/videos.
6. Reconcile source contradictions into bull/bear/unknown scenarios and a risk committee, highlighting stale or missing data. Default **ABSTAIN** without verified predictive evidence; don't auto-place trades.

**Integrated panels:** India Market / Filings / World Risk / Event Clock / Intraday Replay / Strategy Lab / Kronos Bench / Risk Council / Evidence Ledger / Adversarial Review. These are proposed UX panel specs; the CLI returns a structured desk receipt, **not** an implemented full-screen GUI. An AI client renders only supported panels or reports and may optionally open external websites with consent.

**Upstream credits and licence boundaries:**
- Fincept-Corporation/FinceptTerminal — public AGPL and additional commercial licence restrictions. Examine interface concepts only; **never vendor its source or use internal data services commercially without permission**.
- koala73/worldmonitor — AGPL; prefer the official remotely authenticated MCP or REST service, where pricing and data-licensing still apply. Never fork AGPL app source into the proprietary FundTex code.
- Jakeschincariol/day-trader-skill — MIT; general day-trade methodology adapted independently for Indian session mechanics; no upstream Python or private trading automation copied.
All numerical outputs must show sources, as-of, assumptions, negative cases and capability limits.