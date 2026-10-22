# Fundtex v1.0 — Agent-Native India Financial Research Desk

Primary user interface: Claude Code, Codex, Gemini CLI, Cursor or other terminal-enabled coding-agent CHAT. Users never hunt scripts or manage a separate dashboard.

A good one-prompt user request is:

> Analyze Infosys using the freshest available legally permitted Indian financial data, verify actual primary filings where your web tools permit, include an authenticated broker quote if my account is already connected, create a dated technical chart, challenge upside/downside assumptions, and deliver the Excel/CSV/images/PDF research pack with transparent sources.

The agent loads fundtex-auto-analyst and fundtex-india-live-data skills, verifies version and authorization, identifies the actual verified NSE/BSE symbol, and runs the CLI on the user's behalf:

    fundtex research --symbol INFY.NS --source public --quote auto --out /new/approved/fundtex-report

Never require the end user to memorize commands. Ask only for an essential ambiguous ticker, source consent or unavailable credential connection.

## Sources and accurate meanings

| Mode | Actual result |
|---|---|
| Public Yahoo chart endpoint | Dated real historical daily observations, classified UNOFFICIAL_BEST_EFFORT_DELAYED. Not licensed exchange live streaming; timeliness/adjustments unverified. |
| Approved local CSV | Dated historical price series with source hash. Unverified if no original source opened. Explicit SYNTHETIC_FIXTURE input stays fictional. |
| FYERS v3 (eligible FYERS clients, API data features advertised free) | Read-only authenticated quote snapshots and daily OHLCV; per-user app authentication required, token expires daily; not WebSocket streaming inside Fundtex yet. Official: https://fyers.in/api-docs/v3/api/market-data/quotes/ |
| Zerodha Kite Connect | Read-only authenticated REST LTP snapshot when a permitted account and token are configured; not tick-by-tick streaming. Documentation: https://kite.trade/docs/connect/v3/market-quotes/ |
| DhanHQ v2 | Read-only authenticated LTP snapshot using a user-verified security ID and permitted token. Docs: https://dhanhq.co/docs/v2/market-quote/ |
| RBI/SEBI RSS | Official announcement metadata only; agent must actually open dated original notices to verify what changed. |
| Exchange/issuer financials | Original NSE/BSE/issuer published financial statements; NOT retrieved/verified merely by running a chart command. |

Use --source fyers with a permitted FYERS account to fetch actual historical OHLCV for candlestick charts. Use --quote fyers for a separate latest REST quote snapshot.

--quote auto only uses a broker previously configured through authorized local environment. Without one, it reports NO_CONFIGURED_BROKER; it does not fabricate a live price. Explicit --quote kite or dhan is strict and fails closed on missing/invalid auth. A broker snapshot shows retrieval UTC and original trade timestamp only if the source supplies it; a quote retrieved at night can contain the exchange's LAST previous trade.

## Guided broker connection

An authorized Claude/Codex agent first runs `fundtex connect` and asks the analyst for an existing broker, rather than requesting access tokens or sending manual scripts. It offers official Zerodha Kite MCP for supported Claude clients (broker-hosted authorization, no password sharing), FYERS individual-app setup with token expiry, DhanHQ's paid market-data entitlement and Kite Connect developer authorization. It calls `fundtex connect --provider fyers --verify INFY.NS` (or kite/dhan) only after the owner configures approved local credentials. Read-only quote verification must actually return authenticated data before the agent says connected. Broker-status alone reports configuration presence, not entitlement or token validity. Fundtex itself does not implement end-to-end OAuth, retain tokens or automatically consume a third-party Kite MCP session. Official links: https://zerodha.com/products/mcp/ , https://fyers.in/api-docs/v3/getting-started/authentication/ , https://dhan.co/support/platforms/dhanhq-api/how-to-access-dhan-api/ .

## Credential handling

Never paste broker credentials, OAuth secrets, account statements or client records into the chat or public source repo. The authorized local environment may supply:
- FUNDTEX_FYERS_APP_ID and FUNDTEX_FYERS_ACCESS_TOKEN (FYERS app-auth token; renew per their daily expiration policy)
- FUNDTEX_KITE_API_KEY and FUNDTEX_KITE_ACCESS_TOKEN
- FUNDTEX_DHAN_CLIENT_ID, FUNDTEX_DHAN_ACCESS_TOKEN and FUNDTEX_DHAN_SYMBOL_MAP (verified exact ticker → numerical security ID JSON).

Use fundtex broker-status to check if configuration is present, not to print tokens. Broker tokens can expire or lack entitlements. Provider display and redistribution rights govern lawful usage. Production OAuth renewal, exchange-grade tick feeds and commercial redistribution agreements are NOT bundled.

**No-subscription paths (22 Oct 2026):** FYERS advertises free historical and real-time/quote APIs for clients with an authorized app. Official Zerodha Kite MCP is free in compatible assistants, but its REST API and host MCP session do not share credentials. Zerodha Personal Free excludes data, standard retail Connect costs ₹500/month; October 2026 active-trader credits can cover renewal if its brokerage threshold is met. **Zerodha separately advertises free Kite Connect APIs for eligible startups building mass-retail products, subject to contacting/qualifying with Zerodha.** Dhan Data API is ₹499+tax/month. Data redistributions and commercial website displays need independent permission; personal API authorization alone does not establish redistribution rights. Unofficial GitHub NSE wrapper repositories can break and are NOT substitutes for licensed exchange permission. Sources: https://support.fyers.in/portal/en/kb/articles/does-fyers-charge-any-subscription-fees-for-trading-api ; https://smartapi.angelbroking.com/faq ; https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/historical-data-and-live-market-data-payment-plan ; https://dhan.co/support/platforms/dhanhq-api/how-to-access-dhan-api/

## What the one-command research workflow produces

An untouched NEW folder and ZIP: START_HERE.md, source-evidence.json with publisher/age/hash, agent-mission.json for bounded specialist roles, validated price history CSV, historical technical observations CSV, HTML/SVG chart, return distribution SVG, Markdown analyst memo, optional PDF/XLSX/PNG if safe renderers exist, manifest with exact omissions. Authenticated broker quote snapshot JSON appears ONLY if the broker actually provided one. Historical chart and broker LTP remain SEPARATE.

Fundamental earnings, valuations, and sector conclusions must be added by an authorized agent reading original dated primary documents; a market-data chart is insufficient. The agent must conduct an independent skeptic review, compare source definitions and assumptions, and explicitly ABSTAIN when evidence or alpha validation is missing. No live orders or client auto-trading.

## Professional agent acceptance

1. Detect real tools/authorizations and installed version. If old, never silently overwrite personal modifications; request explicit upgrade permission.
2. Use latest lawful public or approved user source. Do not invent synthetic fallbacks after a network failure.
3. Verify observed-as-of date, ticker identity, CSV source and price adjustments.
4. Obtain broker quote only when previously authorized. Never expose credentials.
5. Render pack, check the files actually exist, open graphics/PDF/XLSX as supported, inspect errors and omissions.
6. Cite actual opened original issuer/regulatory documents before making material fundamental claims.
7. Present a concise decision-first result and download links where host supports them.

The optional agent roles are source, financials, macro, quantitative checks, independent skeptic and reviewer/editor. Mission Control designs a bounded plan; actual parallel subworkers depend on host support and permissions.

## Empirical status

A test Mac successfully fetched 64 best-effort Yahoo historical observations for INFY.NS with last observation on 21 October 2026. This proves that particular historical request responded; it does NOT prove an entitled live NSE tick feed or authenticated broker connectivity. Test with real provider credentials only in a user-approved environment; never call mocks real.
