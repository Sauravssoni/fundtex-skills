# Fundtex India: analyst evaluation pack

## Intended evaluator
An investment research professional evaluating an early-stage workflow. This is **not** an exchange-data terminal, SEBI-registered report provider, fund manager or broker integration. Do not use sensitive client account data without the firm's formal approval.

## 20-minute structured evaluation
1. Clone repository and run \`bash install.sh\`; restart Claude Code. Check the 17 skills are discoverable (11 US source skills, 6 India skills).
2. Import an institution-approved dated NSE/BSE equity CSV. Columns \`date,symbol,close\` (optional \`volume,source\`) with exchange suffix \`.NS\` or \`.BO\`. Decide and document whether closes are adjusted for dividends/splits.
3. Run \`fundtex analyze --csv /absolute/path/prices.csv --symbol INFY.NS\`; verify source/date, observation count, worst drawdown, 5% return quantile, tail loss and RSI. Reject any report with data outside the requested ticker.
4. Run \`fundtex portfolio --prices examples/portfolio_prices.csv --holdings examples/holdings.csv\`; verify sources are labelled synthetic, sector weights total 100%, volatility, correlations and variance contributions are reasonable.
5. Run \`fundtex value --inputs examples/valuation.json\`; test a changed WACC and terminal growth. Confirm valuation changes and the engine does not call it a market price.
6. Run \`fundtex news --query 'Infosys NSE earnings'\`. This returns leads, not verified facts. Click through and check exchange filings for any substantive catalyst.
7. Run \`fundtex simulate --csv examples/india_prices.csv --symbol RELIANCE.NS --paths 1000000 --seed 42 --horizon 1\`. Repeat with same seed; results should match except timestamp outside the sim. Explicitly confirm that this does not represent trading performance.
8. Repeat an invalid ticker, missing CSV, duplicate date and unreasonable DCF assumptions. They must be rejected rather than repaired with invented data.

## Sample Claude Code prompts
- "Using fundtex-india-market, study this sourced INFY.NS CSV. State evidence quality, trend, downside quantiles and missing data. Do not recommend trades."
- "Using fundtex-india-portfolio, identify concentration/correlation and the largest contributors to risk across these three NSE positions. Show your assumptions."
- "Using fundtex-india-news, locate fresh company announcements and verify each claim against primary BSE/NSE or company IR documents before writing a 1-page note."
- "Using fundtex-india-valuation, create base/bull/bear scenarios, challenge the FCF margin and reconcile the diluted share count to a current filed disclosure."
- "Assess whether data licensing, SEBI research analyst rules, audit trails, client confidentiality and approval gates permit our intended institutional deployment."

## Analyst scorecard
Grade each 1–5: **Data traceability**, **calculation reproducibility**, **source freshness**, **corporate action treatment**, **valuation defensibility**, **risk explainability**, **India regulatory fitness**, **failure honesty**, **workflow speed**, **integration readiness**. Record every discrepancy with the source timestamp and expected vs actual result. A useful pilot is not a claim of predictive alpha.

## Immediate blockers before real institutional deployment
- Commercial exchange/broker licensed feeds, corporate actions, P/E and quarterly financials with provenance, official announcements and time-series PIT history.
- 3+ years point-in-time walk-forward backtests with corporate actions, survivorship bias, realistic slippage/impact, transaction costs, STT/charges and control portfolios.
- Security/privacy assessment, role-based access, retention, vendor agreements, analyst sign-off, SEBI and legal/compliance sign-off for any external recommendation service.

## Version
Research-preview 0.1, October 2026. Original 11 upstream US skills retained under MIT attribution; India engine is standalone and read-only.
