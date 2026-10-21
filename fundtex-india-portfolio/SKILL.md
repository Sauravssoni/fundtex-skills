---
name: fundtex-india-portfolio
description: India NSE/BSE portfolio risk lab with dated multi-stock prices, weight and sector concentration, daily-return correlations, historical VaR, drawdown and risk contributions. Use for Indian portfolio allocation and analyst risk review.
argument-hint: "[holdings CSV, market price CSV]"
---

# Fundtex India Portfolio Risk

For a **human analyst**, assess INR long-only cash-equity portfolios using verified sourced, adjusted price histories. Do not pretend the sample data is real. The standalone CLI requires holdings `symbol,weight,sector` and price `date,symbol,close` files:

```bash
fundtex portfolio --prices examples/portfolio_prices.csv --holdings examples/holdings.csv
```

Run from installed `$HOME/.local/bin/fundtex` or use `python3 -m fundtex_india.cli` in the Fundtex repository. This is an independent India layer; don't apply US-only broker/tax rules to NSE trades.

## Output checklist

Explain sector concentration, HHI, largest exposure, normalized risk contribution, pairwise correlations, maximum drawdown, historical 5% quantile and tail mean. Disclose date overlap and missing days; no silent forward filling, weights normalization or fake quotes. State that the NAV assumes daily frictionless rebalancing and ignores taxes/slippage, liquidity, transaction costs and implementation feasibility. See broker/exchange disclosures for facts. Never present analytics as investment advice or performance forecast.
