---
name: fundtex-hedged-options
description: Analyze Indian index or stock options iron condors, defined-risk verticals, spreads, collars and other multi-leg payoff structures from approved strikes, actual lot sizes and premium quotes. Use for payoff analysis, risk budgets, costs, scenario stress and broker margin caveats; never place orders.
---

# Fundtex Hedged Options Lab | India research-only

When a user asks to build or optimize an options position, verify underlying identity, official current lot size, expiry, available permitted option-chain prices, option style and settlement regime. Ask only the essential missing number; NEVER infer a live premium, expiry or margin. A permitted broker market-data MCP/REST source is preferable; otherwise clearly use user-approved premiums or fictional examples with a label.

Use the approved locally installed CLI through the coding agent, never ask users to memorize commands:

`fundtex options-sim --inputs /approved/hedged-options.json`

The required specification: `underlying`, `spot` (user-supplied), `lot_size` (user-supplied), `valuation_date`, `expiry_date`, and `legs` with `kind` call/put, `side` buy/sell, `strike`, `premium`, `lots`. Optional `annualized_volatility` and simulation `paths`/seed, plus `max_risk_inr` and named `rates` overrides. Rules are numeric JSON, not executable user code. By default the engine rejects unbounded downside even for research.

Report gross and entry-fee-adjusted net premium, breakevens, model max profit/loss, scenario P&L, payoff against underlying levels and bearish/neutral/bullish cases. Model fees reference 2026 NSE option STT and illustrative Zerodha tariff with explicit provenance; confirm current broker charges and exchange contract details at the time of use. **Warning: the model does not include exercise STT, exit brokerage, margin, slippage, market impact, physical delivery, early assignment, tax position effects or real-time volatility.** Even defined-risk intrinsic structure does not guarantee actual final costs cannot exceed displayed figures.

The optional terminal lognormal simulation is a mathematical scenario under **user-supplied volatility**, not calibrated probability of profit or predicted future market state. Use independent skeptics to challenge premia, assumed volatility, liquidity, settlement and brokerage margin. Hedge designation does not guarantee safe leverage. No broker placement, order previews sent to brokers, GTT, funding or execution.

Helpful source links:
- https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax
- https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies
- https://zerodha.com/charges
