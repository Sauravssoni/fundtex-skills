---
name: fundtex-india-live-data
description: Fetch and verify Indian equity public historical OHLC/adjusted closes from an unofficial documented provider, and read authenticated, authorized broker LTP snapshots from FYERS, Zerodha Kite Connect or DhanHQ. Separate data freshness, source licensing, verification status, ticker identity and real-time streaming limitations.
---

# India Data Desk — Live Quote Snapshots and Historical Evidence

## Public data and real-time distinction

- fundtex research --symbol INFY.NS --source public --out /new/research-folder retrieves dated Yahoo chart history in best-effort mode. Classify UNOFFICIAL_BEST_EFFORT_DELAYED and record original observation date; do not assert exchange data entitlements, original issuer evidence or guaranteed intraday latency.
- fundtex broker-status displays only configuration presence (no key material).
- For FREE eligible FYERS-client authenticated daily candles, use fundtex research --symbol INFY.NS --source fyers --quote auto --out /new/report-dir. This preserves actual OHLCV candles for the chart. FYERS personal developer app access must have permissions and current token; no access is bundled.
- fundtex quote --symbol INFY.NS --provider fyers, --provider kite or --provider dhan reads official authenticated LTP REST **snapshots**, not streaming; no order placement endpoints are present.
- Provider accounts, access tokens and contractual usage rights must be supplied/configured by the authorized analyst through their local system. NEVER request the user paste passwords or tokens into chat. Use only approved local environment/secret handling.
- DhanHQ instrument ID must correspond to an approved exchange symbol in FUNDTEX_DHAN_SYMBOL_MAP; no invented ID fallback. Kite uses NSE:TRADINGSYMBOL or BSE:TRADINGSYMBOL.
- If no credential or source fails, report NO_AUTHENTICATED_PROVIDER or a clear source error; no fake price.



## First-run broker connection — must be conversational

Before asking a new analyst to supply an API token or run a script, call `fundtex connect` for the safe provider-choice catalog. Ask only: "Do you use Zerodha, FYERS, Dhan, or would you prefer public historical data for now?" Explain whether the selected data route is free, subscription-gated or account-specific.

- **Zerodha users in Claude:** Prefer Zerodha's official Kite MCP at https://zerodha.com/products/mcp/ for broker-hosted sign-in and read-only market information when available in that Claude client. Lead them through the official MCP install/authorize UI. Never request passwords or tokens. The Fundtex CLI cannot automatically consume a foreign MCP session; use verified MCP results in the host analyst workflow and keep data source attribution.
- **FYERS users:** Guide them to the official individual-app authentication process (https://fyers.in/api-docs/v3/getting-started/authentication/). Browser approval and secure local token setup are required; never solicit codes/secrets in chat. Then run `fundtex connect --provider fyers --verify INFY.NS` to verify a read-only quote after the user has configured it, and use authorized FYERS OHLCV history.
- **Dhan users:** Guide official Dhan Web Profile → DhanHQ Trading/Data APIs. Explain that market-data entitlement can require a paid subscription and a verified security ID mapping. Never subscribe, charge, or place trades for them.
- **Kite Connect developers:** Direct the user to the official Kite Connect auth documentation and explain the difference from broker-hosted Kite MCP; verify eligible market-data API entitlement.
- **No broker:** Continue with clearly labelled best-effort public dated history, and tell the user what cannot be claimed as live.

Agent must show only ONE next action at a time when guiding authorization, verify a real tool/quote response after consent, and only then say connected. Never claim `broker-status` proves authentication: it checks local configuration presence only.

## Provenance and financial integrity

Check issuer identity, corporate actions, publication times, segment/series, timezone, historical price adjustments, rate limits and legal redistribution. A last-traded price returned from a broker may be old if the exchange is closed; retrieval time does not prove a new trade at that instant. Even full market data does not independently validate company fundamentals. Quote metadata remains separate from historical candle data.

Any real-data claim should point to an actually inspected source or tool result; no trading advice without supporting evidence and appropriate regulatory review.
