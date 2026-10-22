# Fundtex Strategy Lab v1.1 — Strategy Builder, Options Research and Connector Contracts

**Branch-only engineering release, 23 October 2026.** Retains CLI-first, agent-native UX and optional localhost viewer. No production order executor, authenticated financial feed, or broker margin guarantee is included.

## Agent UX

A user says: "Using permitted historical Indian data, build 10/50 and 20/80 moving-average strategies, benchmark on untouched data, stress costs, and give me what could go wrong." Their authorized Claude/Codex/Gemini agent verifies actual NSE/BSE ticker and approved OHLC source, constructs a bounded JSON specification, executes `fundtex strategy-build --csv /approved/real-ohlc.csv --symbol INFY.NS --inputs /approved/strategy.json`, inspects outputs, and explains train selection, honest holdout comparison, source hash, fees and missing evidence. **No user must memorize a script.**

For options: "Build a defined-risk NIFTY put credit vertical using today's *actual authorized bid/ask chain*, explicit lot size/expiry, ₹12,000 budget and stress tests." The agent verifies authorized chain, prompt approvals and data rights, constructs a broker-aware local JSON and invokes `fundtex options-build --chain /approved/option-chain.csv --inputs /approved/limits.json` to score user-file candidates. Then calls `fundtex options-sim --inputs /approved/selected-legs.json` for expiry intrinsic payoff, illustrative fees, optional theoretical Greeks and simulated terminal outcomes. **All underlying and option prices must be provided by a real entitled source or explicitly approved fictional fixture.** A read-only hosted broker MCP may supply data to host memory but does not initialize Fundtex REST CLI credentials.

## Built-in commands

| CLI | Input | Output | Non-goals |
|---|---|---|---|
| `fundtex options-sim --inputs JSON` | User-supplied spot, lot size, valuation/expiry, 1–8 option legs, premium, call/put, side, lots | Gross/net premiums, 2026 *illustrative* entry fee ledger, exact piecewise intrinsic max gain/loss, breakevens, payoff curve, optional simulated terminal prices and BSM sensitivity | Does not fetch an option chain, verify contract margin/settlement, predict returns or execute orders |
| `fundtex options-build --chain CSV --inputs JSON` | Dated, same underlying/expiry/lot user-approved `bid/ask` CSV + explicit width/capital limits | Credit put/call vertical candidate ranking based on *model intrinsic reward/loss*, bid-to-sell and ask-to-buy, source hash and stress levels | No implied probability-of-profit and no "best trade" recommendation; no multi-leg fill certainty |
| `fundtex strategy-build --csv OHLC --symbol TICKER --inputs JSON` | Genuine timestamped OHLC and bounded SMA/RSI rules, cost bps | Training-only parameter selection, untouched chronological holdout, next-open trading assumptions, matched passive baseline, risk metrics and 2x/4x cost stress | No close-only fake fills, no alpha claim, no trading, no true Indian brokerage fee ledger in this v1 |
| `fundtex integrations` | No broker secrets, no network | Provider/tool catalog, optional SDK and local credential *presence* separate from authenticated connection | Cannot connect accounts or install SDKs on its own |

### Example fictional options specification

```json
{
  "underlying":"NIFTY",
  "spot":25000,
  "lot_size":75,
  "valuation_date":"2026-10-23",
  "expiry_date":"2026-10-29",
  "data_quality":"SYNTHETIC_FIXTURE",
  "require_defined_risk":true,
  "max_risk_inr":12000,
  "annualized_volatility":0.20,
  "paths":10000,
  "legs":[
    {"kind":"put","side":"sell","strike":25000,"premium":150,"lots":1},
    {"kind":"put","side":"buy","strike":24800,"premium":90,"lots":1}
  ]
}
```

**All quantities above are illustrative, not current chain values, an exchange-confirmed lot size or an NSE-listed valid expiry.** Premium inputs and implied volatility in real market conditions require separate verification. Source data should be timestamped and contract-specific.

For a chain CSV the fields are `symbol,expiry,kind,strike,bid,ask,lot_size,as_of`. The builder refuses crossed quotes, duplicates, expired snapshot dates, mismatched lot sizes, broad searches and incompatible underlyings. Example rules JSON is in `examples/strategy_rules_SYNTHETIC.json`, and example option legs JSON is in `examples/options_put_credit_SYNTHETIC.json`.

## MCP data access

The existing optional Fundtex MCP server exposes bounded *local-only file tools* via the official MCP Python SDK v2. This new work adds `fundtex_options_expiry`, `fundtex_options_spread_builder`, `fundtex_strategy_backtest`, and `fundtex_connector_status` alongside original sources/regulatory/AMFI/diligence/pilot tools. Set `FUNDTEX_APPROVED_DATA_DIR` to an **explicitly user-approved directory** and install SDK `mcp>=2,<3` in an isolated permitted environment. The server starts with `python3 -m fundtex_india.mcp_server` and uses **stdio**, not a publicly exposed HTTP endpoint. Only inspect/install into the actual user's host after consent; the source code cannot register itself as a tool in all AI clients. Tools require approved relative paths, reject symlinks/escaping and bound config JSON at 64 KiB. Limit authorizations and never transmit client files to third-party routers.

Optional read-only data layers, **not installed or verified connected by this commit**:

- Official Zerodha Kite MCP: https://zerodha.com/products/mcp/ , user-authenticated at broker; grant only needed read tools and **exclude GTT and order mutations** regardless of what a server advertises.
- OpenBB MCP: https://docs.openbb.co/odp/v4/python/extensions/interface/openbb-mcp , separate approved install and selected provider extensions; each provider has its own licensed-data terms.
- QuantConnect LEAN: https://github.com/QuantConnect/Lean , Apache-2.0 professional event-driven research tool; use only pre-approved datasets, offline backtests and disabled live-trading connectors.
- FYERS REST: already configured read-only `--source fyers` when an eligible account is authorized, with short-lived credentials kept in the local secret manager.

VectorBT's fair-code Commons Clause may impose commercial redistribution restrictions; do not embed its source to build a paid Fundtex replica without specific license permission: https://pypi.org/project/vectorbt/ . This code uses only Python standard-library calculations.

## Real 2026 costs versus available approximation

The option entry tariff defaults to broker fee ₹20 per leg; option-sale STT of **0.15% of premium from 1 April 2026**; options buy-side stamp duty of **0.003% of premium**; and illustrative brokerage/exchange/SEBI and GST. Official check: https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax and https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies ; broker example https://zerodha.com/charges . Actual broker, exchange segment, product category, execution/expiry timing, DP/SEBI/GST, physical delivery and exercise treatments **must** be independently confirmed. A defined-risk gross payoff can incur additional real-world charges. The historical equities backtester uses a **user-assumed per-position-change bps friction**, which is *not* an exchange/broker-verified tax engine.

## Experimental validity

A high payoff/maximum-loss ratio does not imply profitable odds. Simulated terminal price assumes a *single* user-specified lognormal distribution, not an observed IV skew or calibrated odds; approximate Black–Scholes Greeks are theoretical local sensitivities, not exchange Greeks. Strategy optimizer's parameter selection excludes future holdout from choosing rules, and signals use only completed closes with next real opens. Holdout still has multiple-comparison risk and single-regime limitation; results cannot certify repeatable alpha.

A professional approval demands: exchange-authenticated contract/lot/expiry master, bid/ask time alignment and realistic multi-leg fill simulation; real F&O historic IV/skew/Greeks, fees, physical settlement, assignment, margin and closing leg costs; untouched year/sector/regime holdouts and walk-forward revalidation; independent security tests; legal approval for advisory/retail algos/MTF and any product trade actions. No order placement code is in this branch.

## Read-only release tests

Run `python3 -m unittest discover -s tests -p 'test_fundtex*.py'`, `RUN_MILLION_TEST=1 python3 -m unittest tests.test_fundtex_million`, `python3 -m fundtex_india.cli options-sim --inputs examples/options_put_credit_SYNTHETIC.json`, and `python3 -m fundtex_india.cli integrations`. Source and output facts must be checked for every release; no green claim before the exact commit is tested.

## Executed release evidence, 23 October 2026

Isolated authorized Mac test root: `/tmp/fundtex-strategy-audit-20261023` on Apple M1 Pro / Python 3.11, with sensitive inherited HOME/environment stripped for unit runs:

- Full `unittest discover`: **133 tests run, 0 failures, 2 skips** (optional Pillow raster and one-million-path stress disabled in regular suite).
- Explicit `RUN_MILLION_TEST=1`: **1,000,000 synthetic random draws PASS in 3.92s**. This is runtime and numerical determinism, not trading alpha.
- Synthetic 2-leg NIFTY put-credit-spread CLI: PASS, including bounded payoff, modeled 2026 entry charges, theoretical aggregate Greeks and 10,000 seeded terminal scenarios. It displays `SYNTHETIC_FIXTURE`, has no authenticated broker feed and cannot place orders.
- Bid/ask CSV vertical scanner: pure-math tests for put/call spread structure, crossed markets, stale date, lot mismatch, duplicate strikes, risk-budget fail-closed; CLI and local MCP functions returned equal outputs on approved synthetic test files.
- Genuine MCP Python SDK v2.3.0 installed **only into** `/tmp/fundtex-mcp-v2-check-20261023`. The public `build_server()` constructed successfully as `MCPServer`, and `list_tools()` returned the ten expected source, mission, regulatory, AMFI, diligence, pilot, status, options, vertical-scanner and strategy-backtest tools. This verifies schema construction; no host session, external OAuth, data feed or account entitlement has been authenticated.
- The host's preinstalled generic `mcp` module did **not** expose v2 `MCPServer`; global Python was left unchanged. Consumers need an isolated MCP v2 env or equivalent verified host runtime.

**Not verified**: real options chain quotes or expiry conditions, historical Indian options-chain backtest, exact post-tax/settlement risk, consistent exchange data licensing, deployed website and authentication, securities registration, profitable alpha, full browser visual QA or a production-grade installed host MCP connection.

**Release decision**: draft research engineering PR; no merge to public main or trade execution until independent empirical, security, compliance and data audits.
