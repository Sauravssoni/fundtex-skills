# Fundtex v1.0.2 — Release audit, 22 October 2026

## One prompt, agent-native first

A user speaks naturally to their authorized terminal-enabled Claude Code, Codex or supported AI agent. The agent reads AGENTS.md and the fundtex-auto-analyst skill, checks existing source connections, and runs the research flow and verifies the actual output files. No second dashboard is required. Running the same CLI directly WITHOUT an AI agent is also supported. A plain web-only chat cannot install software or execute tools without access.

Broker onboarding must check existing authorized data tools before asking. If none are connected, ask ONE short choice of Zerodha, FYERS, Dhan or public-history mode. Broker-controlled login/2FA and paid entitlement approval belong to the human user on the official broker domain. Never request login passwords, access tokens or OAuth authorization codes in chat. Kite MCP tool access remains in its user-authorized host; it is NOT an automatic FYERS/Kite Connect/Dhan environment token for Fundtex Python.

## Actually tested

- Real public price fetch: INFY.NS returned 247 historical observations dated through 22 October 2026 from a best-effort Yahoo Finance chart request in approximately 3.4 seconds on one Mac. Source quality is UNOFFICIAL_BEST_EFFORT_DELAYED; not a guaranteed real-time exchange feed.
- End-to-end one-company research pack: real data produced HTML and SVG chart, historical CSV, Markdown memo, source ledger, PNG raster, research mission plan and compressed ZIP. Mac lacks optional artifact_tool and ReportLab packages and Chromium runtime, so XLSX/PDF/browser screenshot were honestly omitted there.
- Broker quote/authorized history: FYERS, Zerodha Kite Connect and DhanHQ have mock-tested strict REST adapters and credential-failure guards. Actual client-authenticated live quotes and authorized FYERS OHLCV have NOT been tested against a real connected user account. Broker REST LTP snapshots are not continuous WebSocket ticks.
- Indicators: SMA20/50, EMA12/26, RSI14, historical crossings, manual lines/zones and vector charts. Fixed the flat-price RSI edge case: it now reads neutral 50 instead of 100.
- Risk and downside: separate historical tail-risk JSON, backtested cost-assumption walk-forward evaluation, cautious chronological forecast-validation where observations are sufficient. The user must inspect ABSTAIN and uncertainty gates; none of this independently proves future trading alpha.
- News: best-effort public headline RSS metadata, keyword-only topic flags and explicit disclaimers about unverified original articles. No article-level trustworthy NLP sentiment, no automatic primary issuer filing verification.
- Agent planning: source/financial forensics/macro/quant/skeptic/editor plans are generated. Actual parallel specialist execution depends on the Claude/Codex host having subagent tools, permissions and context; a saved mission plan is NOT executed agents.

## Known limits preventing a certified Bloomberg-equivalent claim

No contractually licensed continuous Indian exchange feed is included; no automatic historical corporate-actions/point-in-time statement database; no completed real broker OAuth/account integration; no verified stock forecasting alpha; no automatic regulatory filing fact authentication or private cross-host memory sync; no installed default PDF/XLSX renderer guarantee. These require actual account entitlements, source agreements and independent production QA.

## The intended first-run prompt

Analyze Infosys using the freshest legitimately permitted Indian market sources. Use Fundtex automatically. Check for my authorized brokerage connection; if none is available, offer an official guided connection or continue with dated public historical prices. Create an actual chart, risk and downside review, cautious forecast validation, news-topic monitoring, source ledger, Excel/PDF when available and a finished research ZIP. Check the outputs and tell me exactly what remains unverified. Do not ask me to hunt for scripts.

The background CLI implementation is: fundtex research --symbol INFY.NS --source public --quote auto --out /new/approved/report-folder. Public historical mode includes unverified public news discovery by default (can be disabled using --no-news). Authorized private CSV mode never sends a news query unless the user explicitly requests --with-news.

## Launch policy

Research preview can be released after regression and ZIP QA pass. An institutional-grade launch or Bloomberg replacement claim additionally needs real broker authorization, data license validation, external financial analyst scorecards and live market-data quality measurements. Synthetic millions of calculations are NOT evidence of real stock prediction profitability.
