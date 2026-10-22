# Fundtex Broker Connection Guide — Agent-Native

Fundtex is a skill and CLI-based assistant. The user talks naturally to Claude, Codex, Gemini or a supported coding agent. The agent runs the commands and guides authentication conversationally.

## Broker selection

Internal agent command:

    fundtex connect

Ask a single question: Which broker do you currently use — Zerodha, FYERS, Dhan, or none? Continue with real but unofficial best-effort historical data when no broker is connected. Never substitute synthetic current prices.

## Zerodha Kite MCP — easiest for Claude

Official: https://zerodha.com/products/mcp/
Support: https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/connect-zerodha-ai-assistant

Zerodha advertises free broker-hosted MCP access for supported Claude/Cursor clients. The user follows Zerodha's official browser login and consent. Never request passwords or API keys in chat. The agent must actually inspect and use the connected host's Zerodha tool output before saying it has real prices.

IMPORTANT: Kite MCP inside Claude is NOT automatically available as a Fundtex Python CLI market-data source. The agent can use verified host-MCP results in its research; no independent automatic cross-connector bridge is claimed.

## FYERS personal developer app

Official: https://fyers.in/api-docs/v3/getting-started/authentication/

The account holder authorizes an individual FYERS app in the official browser with a controlled redirect URI. The official authorization-code flow generates an access token, which expires daily. Store the App ID and access token only in an approved local secret facility (environment names: FUNDTEX_FYERS_APP_ID, FUNDTEX_FYERS_ACCESS_TOKEN). Never put access tokens, app secrets or redirect authorization codes in the chat.

After the user's local setup is complete and permission to check prices is confirmed, the agent verifies with:

    fundtex connect --provider fyers --verify INFY.NS

If successful, the authorized agent can use:

    fundtex research --symbol INFY.NS --source fyers --quote fyers --out /new/approved/analyst-report

This provides authenticated daily OHLCV candles and a separate LTP snapshot; it does NOT continuously stream quotes.

## Zerodha Kite Connect developer app

Official: https://kite.trade/docs/connect/v3/user/

Separate from Kite MCP. Confirm the user's API market-data entitlement and any applicable plan charges. Use Zerodha's approved browser app login and locally managed FUNDTEX_KITE_API_KEY and FUNDTEX_KITE_ACCESS_TOKEN. After user consent, verify:

    fundtex connect --provider kite --verify INFY.NS

Do not assume that a free Kite brokerage account grants the developer data API.

## DhanHQ v2

Official: https://dhan.co/support/platforms/dhanhq-api/how-to-access-dhan-api/

Through the account holder's Dhan Web browser: Profile > DhanHQ Trading/Data APIs. Current Dhan guidance lists market Data APIs at ₹499 plus taxes monthly; paying or subscribing requires explicit approval. Generate an official token. Locally store FUNDTEX_DHAN_CLIENT_ID, FUNDTEX_DHAN_ACCESS_TOKEN and FUNDTEX_DHAN_SYMBOL_MAP using actual verified Dhan security IDs. The agent can then verify a read-only quote with:

    fundtex connect --provider dhan --verify INFY.NS

No trading endpoints are exposed by Fundtex's broker quote tools.

## Claims and privacy

- broker-status checks whether credentials are configured, not whether they are valid or entitled.
- connect --verify attempts one authenticated read-only LTP request, if configured. Only a successful actual provider response earns a connected status.
- No passwords/tokens/auth codes should be requested in chat, logged, bundled with reports or committed to Git.
- Last-traded price is not the same as streaming tick-by-tick data, and may be from a previous trading session.
- No auto-OAuth, automatic broker billing, paid plan activation, token refresh, order placement, private-account import or unapproved client-data transmission.
- If any provider is unavailable, keep the historical research workflow available and disclose missing live data.

## Agent-level handoff contract

The agent should ask which broker, guide only that broker, verify it where its host permits, then independently perform actual dated research and a report pack. The user should never have to hunt a script. Source-document verification, chart exports, PDF/Excel optional dependency checks, and independent skeptic review remain mandatory before institutional claims.
