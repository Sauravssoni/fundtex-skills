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

## Easiest account connection: broker-hosted MCP, not pasted API tokens

For a Zerodha user using Claude, follow docs/BROKER_CONNECTION_ASSISTANT.md: prefer the **official Kite MCP** remote endpoint https://mcp.kite.trade/mcp, via the host's supported MCP registration flow and the user's official browser consent. This broker-hosted connection is advertised FREE by Zerodha; it is not the same as a paid Kite Connect developer market-data API. Do not request Zerodha passwords or access tokens in the AI chat.

When already authorized, call the actual read-only Kite market-data tools, check symbol + published timestamps, and hand user-permitted historical OHLCV to Fundtex charting. Do NOT pretend Kite MCP populates the CLI's FUNDTEX_KITE_* credential environment. If the host does not support MCP, explain that limitation and offer existing approved CSV, FYERS or public delayed data rather than a fake live feed.

DhanHQ data APIs require an active Data subscription (published ₹499 + applicable taxes/month), and Dhan individual access tokens commonly expire after 24 hours. The agent must guide setup on web.dhan.co, not auto-subscribe or handle secrets in chat. Its community agent-skill bundle includes order execution; use only Fundtex's read-only data connector unless user has separately authorized a trading integration. For FYERS use the permitted account/app authorization path. A real broker auth test needs the user's action and cannot be proven by parser unit tests.

## Provenance and financial integrity

Check issuer identity, corporate actions, publication times, segment/series, timezone, historical price adjustments, rate limits and legal redistribution. A last-traded price returned from a broker may be old if the exchange is closed; retrieval time does not prove a new trade at that instant. Even full market data does not independently validate company fundamentals. Quote metadata remains separate from historical candle data.

Any real-data claim should point to an actually inspected source or tool result; no trading advice without supporting evidence and appropriate regulatory review.
