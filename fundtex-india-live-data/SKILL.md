---
name: fundtex-india-live-data
description: Fetch and verify Indian equity public historical OHLC/adjusted closes from an unofficial documented provider, and read authenticated, authorized broker LTP snapshots from Zerodha Kite Connect or DhanHQ. Separate data freshness, source licensing, verification status, ticker identity and real-time streaming limitations.
---

# India Data Desk — Live Quote Snapshots and Historical Evidence

## Public data and real-time distinction

- fundtex research --symbol INFY.NS --source public --out /new/research-folder retrieves dated Yahoo chart history in best-effort mode. Classify UNOFFICIAL_BEST_EFFORT_DELAYED and record original observation date; do not assert exchange data entitlements, original issuer evidence or guaranteed intraday latency.
- fundtex broker-status displays only configuration presence (no key material).
- fundtex quote --symbol INFY.NS --provider kite or --provider dhan reads official authenticated LTP REST **snapshots**, not streaming; no order placement endpoints are present.
- Provider accounts, access tokens and contractual usage rights must be supplied/configured by the authorized analyst through their local system. NEVER request the user paste passwords or tokens into chat. Use only approved local environment/secret handling.
- DhanHQ instrument ID must correspond to an approved exchange symbol in FUNDTEX_DHAN_SYMBOL_MAP; no invented ID fallback. Kite uses NSE:TRADINGSYMBOL or BSE:TRADINGSYMBOL.
- If no credential or source fails, report NO_AUTHENTICATED_PROVIDER or a clear source error; no fake price.

## Provenance and financial integrity

Check issuer identity, corporate actions, publication times, segment/series, timezone, historical price adjustments, rate limits and legal redistribution. A last-traded price returned from a broker may be old if the exchange is closed; retrieval time does not prove a new trade at that instant. Even full market data does not independently validate company fundamentals. Quote metadata remains separate from historical candle data.

Any real-data claim should point to an actually inspected source or tool result; no trading advice without supporting evidence and appropriate regulatory review.
