# Fundtex Broker Connection Assistant — Claude-first, secure, read-only

**Default experience:** A user sends an ordinary financial-analysis request to Claude Code, Codex, Cursor or a compatible agent. Fundtex must identify the broker situation, guide the authorized login once, and then do the analysis and output generation. The user is NOT required to read documentation, run Fundtex scripts, locate provider keys or paste sensitive credentials into chat.

This is not a separate onboarding project or a request for another introduction: it is part of the very first real analysis inside the user's existing agent chat.

## Agent first-use dialogue

Do not repeat introductory messages already delivered to the user. Check which market-data tools and accounts are ALREADY connected before asking. Only if nothing usable is found, ask exactly one natural question:

> I can prepare the report using public delayed historical data now. For authenticated Indian market data, do you use Zerodha, Dhan or FYERS? I can walk you through a secure connection to the official provider; you won't have to share credentials in this chat.

If user chooses public data only, proceed immediately with the existing Fundtex research and deliverable workflow. If user chooses a broker, confirm permission to configure only the agreed data connection. Broker connections are user actions and cannot be completed without a login/consent step.

## First choice: Zerodha, official Kite MCP

There is an official, broker-hosted Kite MCP endpoint at https://mcp.kite.trade/mcp. Its stated use includes real-time stock market information and read-only account/market tools. Zerodha describes the Kite MCP connection as free; this is DISTINCT from buying a developer-facing Kite Connect API subscription, currently ₹500/month for individual developer market-data API access. For a personal research assistant use Kite MCP before proposing a paid developer API.

### Claude Code (authorized local terminal)

If the user explicitly agrees to adding the official server and the host permits it, check whether it is already installed. Only if missing, perform:

    claude mcp add --transport http --scope user kite https://mcp.kite.trade/mcp

Do NOT write a project-scoped MCP config into the Fundtex public repository, or edit another existing server without inspecting and confirming. For clients whose HTTP transport does not work, consult the official Kite/host documentation before using any compatibility transport. Check:

    claude mcp list

Then ask the USER to finish the official Zerodha consent in their browser. The agent must not request passwords, 2FA codes, request tokens or API secrets. In the Claude Code session, verify the connected Kite tools using /mcp. Do not report "connected" until a permitted read-only quote request actually succeeds for a verified NSE/BSE instrument and the returned ticker, provider and quote timestamp (if provided) are inspected.

### Claude Desktop

Use the official Zerodha documentation at:
https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/connect-zerodha-ai-assistant

The published Desktop example registers a local connector with an npx mcp-remote wrapper pointed at https://mcp.kite.trade/mcp. Ask permission, inspect the existing Claude Desktop config (never clobber other servers), write only the needed server entry, have the user restart Desktop and sign in at Zerodha's own web page. Do not claim a Claude Code config is interchangeable with Desktop JSON.

### Other agents

Claude Code, Codex, Cursor and VS Code have DIFFERENT MCP registration commands. Inspect the host's actual MCP capability; prefer HTTP remote server at https://mcp.kite.trade/mcp if the client supports it, else follow the official broker configuration. Never claim unsupported host integration.

### Boundary of available data

Kite MCP tools are independent from Fundtex CLI environment variables. Connecting Kite MCP does NOT populate FUNDTEX_KITE_API_KEY/FUNDTEX_KITE_ACCESS_TOKEN. For reports, have the agent explicitly obtain permitted history/quotes with connected Kite MCP tools, reconcile symbol, timestamps and source, and, if authorized by the user and vendor terms, normalize returned historical rows into a local bounded source CSV for Fundtex chart/analyst-pack commands. A separate real-time quote is NOT part of a historical candle series and must not overwrite chart data. If Kite MCP cannot expose the required historical observations, use a declared approved alternative; no synthetic replacement.

**No trading:** Even if MCP presents GTT or trade-related tools, Fundtex research MUST NEVER call create/modify/cancel GTTs, orders, funds or positions. Only approved data/read tools. Never ask for authority to transact as a prerequisite for research. Request only the minimum necessary account data and do not export private portfolios to external providers.

## Dhan — authorized market-data APIs (not free by default)

The user must sign in to official Dhan Web themselves: https://web.dhan.co → Profile → Get Trading & Data APIs. Dhan distinguishes free trading APIs from its Data APIs; the Data API is advertised at ₹499 plus applicable taxes/month and may renew from the trading ledger. Explain the price, renewal and consent before any subscription purchase. Do not subscribe/pay on behalf of the user without explicit approval.

An authorized Dhan individual can generate a token with a typical validity of 24 hours. The account client ID, token and exchange security IDs must be stored ONLY in authorized local secret facilities/environment, NEVER in an AI prompt, a Git repository or public skills, and never echoed in output.

Existing Fundtex quote command reads Dhan credentials when configured. Official instrument master: https://images.dhan.co/api-data/api-scrip-master.csv. The agent may use the official security list via permitted data access to resolve symbol→security ID, checking NSE/BSE, ISIN and segment. Do not guess a security ID.

The separate official-community DhanHQ agent-skill repository has trading-capable tools; do not install/enable full trading capabilities automatically just to view quotes. Prefer Fundtex's read-only market-data adapter and rights-bounded report engine.

Sources:
https://dhanhq.co/docs/v2/authentication/
https://dhanhq.co/docs/v2/market-quote/
https://dhan.co/support/platforms/dhanhq-api/how-to-access-dhan-api/

## FYERS — eligible client API access

If user already has a permitted FYERS account/developer app, use the Fundtex FYERS authenticated quote and historical OHLCV adapters. Agent guides the user through official FYERS developer app authorization using their own device, stores credentials in local approved secret facility, validates a read-only quote then generates candlestick charts. FYERS access token expiry and entitlement must be checked. Do not assume a live account or expose keys in AI chat.

## Decision-first report execution

After a read-only source is ACTUALLY confirmed:

1. Verify ticker and security identity from primary exchange/issuer evidence; do not assume an ambiguous company name.
2. Collect an approved dated historical series with actual OHLC if available. Use fresh, current brokerage snapshots separately, with retrieval time and publisher trade timestamp when supplied.
3. Ask Fundtex to generate a source-hashed interactive chart, technical statistics, price history CSV, relevant risk comparisons, and PDF/XLSX/PNG where optional renderers exist. The agent executes commands, not the user.
4. Use official issuer filings and original RBI/SEBI/exchange documents for financial statements; do not infer earnings or valuation from a price chart.
5. Run skeptical second-pass checks and return a download-ready report with exact data rights, dates and any missing source.
6. If broker connection requires user action, offer a productive public-history report while waiting for login, without mislabeling the source as live.

## Security and verification gates

- Never read or reveal secrets in tool logs, console transcripts, summary JSON, prompts or report artifacts.
- Never place any order, alter GTTs, authorize trading, purchase subscriptions or perform irreversible account actions as a side effect of research.
- Never treat a market-data feed returned through an unofficial wrapper as exchange-certified.
- No broker credential or entitlement is assumed. Mock tests validate parsers/instructions only, not actual account authorization.
- Recorded source timestamp, issuer identity, corporate actions, licence scope and return permissions determine whether outputs can be shared beyond the account holder.
- Do not make a private user portfolio available to third-party cloud agents unless the user explicitly approves that transfer.

Useful user-facing acknowledgment: "I've connected the authorized read-only market-data tool, verified a quote, and will use it for the requested research. I won't trade or change your account." Say this ONLY after confirming an actual connected read response.

Official Zerodha references:
https://zerodha.com/products/mcp/
https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/connect-zerodha-ai-assistant
https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/what-are-the-charges-for-kite-apis
