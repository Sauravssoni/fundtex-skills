# FundTex Option Chain Desk v1 — Read-only DhanHQ capture and conservative liquidity gate
**Release status: experimental, not live-broker-tested. 23 October 2026.**

## Owner-facing experience

An eligible terminal-enabled Claude/Codex user requests: "Use my authorized Dhan market-data access to analyze NIFTY defined-risk verticals for the selected expiry. Verify the contract master and bids/asks, reject stale or illiquid contracts, calculate theoretical costs, challenge negative scenarios, and **do not trade**."

The agent handles discovery, verification, locally approved config files, capture, spread screening and reporting. It must never claim a broker session exists merely because a plugin skill is installed. It must not ask a human to copy an API token or secret into chat, and cannot automatically enroll in paid broker subscriptions.

## Current authorized technical path

Official provider: https://dhanhq.co/docs/v2/option-chain/ . DhanHQ v2 documents **POST /optionchain**, requiring personal `client-id` and `access-token`, explicit `UnderlyingScrip`, `UnderlyingSeg` and `Expiry`; response provides `data.last_price`, `data.oc.{strike}.{ce|pe}.security_id/top_bid_price/top_ask_price/top_bid_quantity/top_ask_quantity/volume/oi`. It documents **one unique option-chain request per three seconds**. The user/host must respect this limit; this engine makes only one network request for each explicit invocation and never retries secretly.

Actual user permission is required to configure `FUNDTEX_DHAN_CLIENT_ID` and `FUNDTEX_DHAN_ACCESS_TOKEN` securely inside the authorized local host environment. The CLI must never echo credentials. No order, GTT, pledge, margin, payment or withdrawal endpoint is present.

**1.** Agent independently verifies underlying scrip, segment, exact contract lot size and expiry against current broker/exchange instrument master. Do not assume NIFTY's old 75-unit example lots apply to a new contract. NSE contract information: https://www.nseindia.com/static/products-services/equity-derivatives-contract-information .

**2.** Agent creates a SMALL user-approved contract config at an approved path:
```json
{"underlying":"NIFTY","underlying_scrip":13,"underlying_seg":"IDX_I","expiry":"2026-10-29","lot_size":65,"max_strikes":20}
```
**This is an ILLUSTRATION**, not a certified current contract/instrument mapping. The person or a genuinely authorized instrument-master tool must verify every field on the requested date and expiry.

**3.** With explicit authorization and private credentials already configured, agent invokes:
```bash
fundtex dhan-chain-capture --inputs /approved/verified-contract.json --live --out /approved/new-snapshot.csv
```
That single read-only call produces NEW `new-snapshot.csv` and `new-snapshot.receipt.json`, with input payload SHA-256, CSV SHA-256, selected strikes, snapshot ID, local UTC capture time, provider-reported security IDs, source status and excluded missing-bid/ask contracts. No file overwrites; no order placement.

Alternatively, if the user explicitly approves a previously saved genuine Dhan payload, agent invokes:
```bash
fundtex dhan-chain-capture --inputs /approved/verified-contract.json --saved-json /approved/original-payload.json --captured-utc 2026-10-23T06:10:00+00:00 --out /approved/new-snapshot.csv
```
**A saved JSON is NOT authenticated by being formatted like Dhan data.** Original capture time is user-declared, no access-token verification. This path is only user-approved private research. Never pretend it is live.

**4.** Agent creates a bounded strategy screen (no one asks the human to make JSON):
```json
{"underlying":"NIFTY","spot":25000,"lot_size":65,"valuation_date":"2026-10-23","expiry_date":"2026-10-29","structure":"bull_put_credit","min_width":150,"max_width":400,"max_risk_inr":15000,"analysis_at_utc":"2026-10-23T06:10:30+00:00","max_snapshot_age_seconds":180,"max_quote_spread_bps":2000,"min_top_quantity":65,"min_day_volume":1000,"min_open_interest":1000}
```
Then:
```bash
fundtex options-build --chain /approved/new-snapshot.csv --inputs /approved/screen.json
```
The builder checks contract symbol, explicit lot, expiry, date, source, same snapshot ID and timestamp, quote age relative to the declared analysis time, max bid/ask percentage spread in basis points, bid/ask displayed quantity, day volume and open interest; **it also checks the sidecar CSV SHA-256 integrity**. A mismatched or altered CSV is rejected. Note displayed Dhan top quantity uses **provider-reported units**; do not infer whole-lot execution capacity without checking contract units.

**5.** Report theoretical strike-level cost-adjusted payoff and max modeled intrinsic loss, fees, break-evens, stress grid, liquidity rejection counts, *non-verified exchange quote age*, possibility of missing/failing multi-leg fills, settlement/assignment/physical delivery and expiry STT. Always preserve **ABSTAIN / STAY IN CASH** as a valid choice. Never rank by modeled reward/loss as if it were actual expected value or calibrated win probability.

## Known severe caveats

- Dhan documents a local response with bid/ask but **not per-contract exchange update timestamps**. `quote_captured_utc` is time of owner-approved local recording, not proof quotes are fresh or executable. User-declared `analysis_at_utc` is not a signed clock.
- A matched CSV and SHA-256 receipt proves only **local consistency**, not cryptographic source attestation. A malicious actor controlling both can forge an internally consistent pair.
- A current-chain snapshot is not **historical options chain data**; do not backtest options profitability from underlying spot OHLC or adjusted-close charts.
- It does not know actual margin reduction, spread execution, paid subscription entitlements, user broker execution limits, exchange auction/halts, stock physical settlement, exercise STT or exit expenses. Maximum modeled intrinsic expiry loss is **not guaranteed maximum actual loss**.
- It cannot independently verify the NSE permitted-lot CSV or physical instrument master until host/source access is granted.
- Broker auth status remains `NOT_CONFIGURED` unless actual authorized data fetch returns. This release was tested with synthetic broker-shaped responses only.

## Executed release checks

On the connected approved Apple Silicon Mac isolated test clone, the targeted read-only option chain/expiry/anti-spoof/sidecar/CLI tests passed **15/15**, then the full Python suite passed **163 tests, 0 failures, 3 optional skips**. The new data-capture handler is not authenticated live because no user-approved API credentials were supplied.

Research only; no securities recommendation, registered financial advice, licensed data redistribution, or trade permissions.
