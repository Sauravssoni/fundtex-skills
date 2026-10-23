# Zerodha Kite MCP — Live Read-Only Research Acceptance Gate
Date: 2026-10-23. **Feature branch only; no production trading.**

## Account-holder test sequence

The developer's account has completed Zerodha Re-KYC and is intentionally zero-funded. Zero funds are not a substitute for eliminating unsafe APIs. The official hosted Kite MCP `https://mcp.kite.trade/mcp` was registered by ChatGPT web as a **custom app without MCP-layer OAuth**. Its `login` tool returns a broker-owned authorization link; the account holder must follow the Kite login page and approve the session. We never copy passwords, TOTP, PIN, account IDs or tokens into chat, GitHub, artifacts or FundTex logs.

**Status verification is explicit:** `MCP_REGISTERED` → `KITE_LOGIN_LINK_CREATED` → `ACCOUNT_AUTHORIZED_IN_BROWSER` → `READ_ONLY_LTP_VERIFIED` → `DATED_OHLC_VERIFIED` → `STRATEGY_INPUT_RECONCILED`. These states are not interchangeable. A browser toast 'connected' does NOT indicate the Kite market-data session is authenticated.

Only direct broker-tool calls `get_ltp`, `get_ohlc`, `search_instruments`, `get_historical_data` and (when necessary) `get_quotes` may be used in this test. Never invoke `place_order`, `cancel_order`, `modify_order`, `place_gtt_order`, `modify_gtt_order`, `delete_gtt_order`, or expose private margins, holdings, positions and profile for public research. The actual hosted server's registration advertises trading tools despite marketing claims; FundTex must provide a **server-enforced read-only gateway** before claiming production-safe web account connections.

### Test 1 — verify one quote

Use the genuine connected `FundTex Kite` MCP:
`get_ltp({"instruments":["NSE:INFY"]})`.
If it replies `Please log in first using the login tool`, **NOT AUTHENTICATED**. Generate a fresh `login` link only upon user request/consent, never assume successful browser authentication. Capture tool name and actual retrieval timestamp; if publisher trade time is absent, do not call it exchange-fresh.

### Test 2 — historical candlestick source

Use `search_instruments({"query":"NSE:INFY","filter_on":"id","limit":10})` and select the exact NSE equity record, verifying `instrument_token` against that returned instrument. Obtain a bounded calendar-specific result via
`get_historical_data({"instrument_token":<actual returned token>,"from_date":"YYYY-MM-DD 09:00:00","to_date":"YYYY-MM-DD 16:00:00","interval":"day","continuous":false,"oi":false})`.
Do not substitute guesses for instrument IDs. Do not request account data or options history without contract-specific eligibility.

### Test 3 — import/calculate without data leakage

The pure Python `fundtex_india.kite_mcp_research` module accepts only approved market-data outputs, no credentials. The agent passes an approved authorized response file to:

```bash
fundtex kite-mcp-import --mode history --file /approved/kite-candles.json --symbol INFY.NS \
  --instrument-token ACTUAL_ID --from-date YYYY-MM-DD --through-date YYYY-MM-DD --out /approved/NEW-kite.csv
```

This explicitly validates finite prices, OHLC geometry, dates, duplicate bars, volume, exact instrument identity and computes a source-bound SHA-256 receipt; no overwrites. It flags `USER_APPROVED_KITE_MCP_PAYLOAD_NOT_EXCHANGE_SIGNED`: importing JSON does not itself cryptographically prove broker source. Run `fundtex strategy-build` with predeclared research rules, chronological holdout and costs; report losing cases. Use the same dated CSV to render source-labelled chart and film. A screenshot is a style guide only, never a substitute for candles.

### Test 4 — numerical regime and million-path benchmarks

Only after actual dated candles pass reconciliation: run the predefined SMA/RSI candidate family, train-only selection, strictly separate holdout, a 2×/4× execution-cost sensitivity and bootstrap sampling uncertainty. Run the one-million-path synthetic benchmark separately. Monte Carlo paths are hypothetical terminal prices, not observed trades, and cannot demonstrate predictive alpha. Current Kite historical spot candles do **not** provide point-in-time options chains, bid/ask, IV skew, expiry settlement or broker executable margins. Do not advertise historical options backtests without separately entitled option-chain data.

## Evidence/provenance and hard release blocks

- No raw account payload, credentials or personally identifiable details in Git commits or public CI.
- No quotes from another symbol, timestamps from future, fabricated opening prices, or mixed adjusted/unadjusted candles.
- Do not publish market data in public repo or expose it to unapproved hosted rendering services. Follow Kite market-data redistribution terms.
- **Server-enforced tool elimination** is a release blocker for one-click ChatGPT web onboarding. Client-side instructions and approval prompts alone do not meet the requirement.
- Provider session binding is not guaranteed. Known issue report in Zerodha upstream: https://github.com/zerodha/kite-mcp-server/issues/82. A login page success can still leave the tool session unauthenticated.
- For a production signup, separately verify tool-level schema, user-consent/revocation, minimal scopes, expiration/reconnect, logging, rate limiting, market holiday behavior, corporate-action adjustments, source timestamps, secrets isolation, and read-only security testing.

This receipt documents the safe acceptance protocol, NOT an already authenticated data feed.
