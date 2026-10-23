---
name: fundtex-hedged-options
description: Analyze Indian index or stock options iron condors, defined-risk verticals, spreads, collars and other multi-leg payoff structures from approved strikes, actual lot sizes and premium quotes. Use for payoff analysis, risk budgets, costs, scenario stress and broker margin caveats; never place orders.
---

# Fundtex Hedged Options Lab | India research-only

When a user asks to build or optimize an options position, verify underlying identity, official current lot size, expiry, available permitted option-chain prices, option style and settlement regime. Ask only the essential missing number; NEVER infer a live premium, expiry or margin. A permitted broker market-data MCP/REST source is preferable; otherwise clearly use user-approved premiums or fictional examples with a label.

Use the approved locally installed CLI through the coding agent, never ask users to memorize commands:

`fundtex options-sim --inputs /approved/hedged-options.json`

The required specification: `underlying`, `spot` (user-supplied), `lot_size` (user-supplied), `valuation_date`, `expiry_date`, and `legs` with `kind` call/put, `side` buy/sell, `strike`, `premium`, `lots`. Optional `annualized_volatility` and simulation `paths`/seed, plus `max_risk_inr` and named `rates` overrides. Rules are numeric JSON, not executable user code. By default the engine rejects unbounded downside even for research.

For a timestamped, explicitly approved option-chain CSV, the agent can discover candidate **verticals** through `fundtex options-build --chain /approved/chain.csv --inputs /approved/risk-budget.json`; it uses assumed sell-at-bid/buy-at-ask, bounded expiry/lot/width checks, risk-budget filtering and no forecasts. `bull_put_credit` and `bear_call_credit` are supported; an iron condor may be evaluated as hand-selected four legs with `options-sim` but is NOT auto-enumerated. This scan is not a broker executable multi-leg order or a margin guarantee.

Report gross and entry-fee-adjusted net premium, breakevens, model max profit/loss, scenario P&L, payoff against underlying levels and bearish/neutral/bullish cases. Model fees reference 2026 NSE option STT and illustrative Zerodha tariff with explicit provenance; confirm current broker charges and exchange contract details at the time of use. **Warning: the model does not include exercise STT, exit brokerage, margin, slippage, market impact, physical delivery, early assignment, tax position effects or real-time volatility.** Even defined-risk intrinsic structure does not guarantee actual final costs cannot exceed displayed figures.

The optional terminal lognormal simulation is a mathematical scenario under **user-supplied volatility**, not calibrated probability of profit or predicted future market state. Use independent skeptics to challenge premia, assumed volatility, liquidity, settlement and brokerage margin. Hedge designation does not guarantee safe leverage. No broker placement, order previews sent to brokers, GTT, funding or execution.

Helpful source links:
- https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax
- https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies
- https://zerodha.com/charges

## 2026-10-23 Monte Carlo convergence & sensitivity upgrade

The `options-sim` model now permits **at most one million** seeded terminal-lognormal paths, explicitly bounded to avoid unapproved resource use. Agent can run 10k first, then up to 1m only when user requests a high-confidence numerical sensitivity check. The result includes **Wilson 95% sampling intervals** around the simulated positive-P&L frequency and approximate mean-P&L standard-error intervals. **Those are conditional on the specified model and premiums, NOT confidence intervals for market outcomes.** Show model uncertainty by recomputing at materially different implied/historical volatility assumptions; use actual chain source/IV only if authorized and separately observed. If a 60% simulated win rate accompanies negative mean P&L, prominently state the negative finding.

User-approved premiums, lot size and expiry are never automatically marked broker-verified. This expiry-only engine omits exercise STT, broker margin, physical settlement, skew, basis/forward, exit fills, transaction costs after opening and portfolio correlation. Required operational risk checks remain separate from the theoretical capped-payoff geometry.

## Broker-entitled Dhan option-chain capture and conservative risk gates (23 October 2026)

**No manually assembled JSON for the end user.** In a coding host with explicit owner authorization, the agent verifies actual broker instrument IDs, expiry and permitted exchange contract lots, captures exactly one DhanHQ v2 read-only option-chain snapshot via `fundtex dhan-chain-capture`, and invokes `fundtex options-build` with safety filters on its SHA-256 receipt. The new data-only adapter requires Dhan's real client ID and access token in the *private approved local environment*, never in chat. It provides a `--saved-json` mode ONLY with user-declared original UTC capture time and never marks saved data broker authenticated. Refuse forged, mixed, old, crossed, illiquid, unverified or edited quote files. Source consistency means local SHA-256 equality, NOT exchange-signed or executable quotes. Dhan's documented response does not include the last exchange-update timestamp per option, so local capture age does not prove market freshness.

Strictly opt-in. Never submit trades or use margin, GTT, pledge or fund APIs. Source guide `$HOME/.local/share/fundtex-intelligence/docs/DHAN_OPTION_CHAIN_DESK_V1_2026-10-23.md` after the approved feature branch is installed, or https://github.com/Sauravssoni/fundtex-skills/blob/feature/options-chain-dhan-quality-gates-20261023/docs/DHAN_OPTION_CHAIN_DESK_V1_2026-10-23.md .
