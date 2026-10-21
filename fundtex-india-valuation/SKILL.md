---
name: fundtex-india-valuation
description: >-
  Build explicit-assumption discounted cash-flow scenarios with sensitivity; cross-check company disclosures, avoid pretending hypotheses are filed facts. Use when a user requests Indian stock/equity analysis, NSE/BSE research, institutional investment evaluation or analyst briefing.
argument-hint: "[NSE/BSE symbol, India sector or data file]"
---

# India Fundamental Valuation | Fundtex Financial Intelligence

**Company:** Fundtex Financial Intelligence, a Syntheon Technology Private Limited financial research initiative. **Status:** research preview, supervised analyst use only.

## Working method

1. Determine NSE (`.NS`) or BSE (`.BO`) symbol and time horizon; identify data ownership, source and currency (INR).
2. Prefer licensed exchange/broker CSV and primary company filings. Explicitly mark `USER_SUPPLIED_UNVERIFIED` CSV until checked. Use `--live` only for unofficial delayed Yahoo daily history, never represent it as live exchange-certified data.
3. Reproduce analysis with the stdlib CLI (from the Fundtex repo or installed launcher):

```bash
fundtex value --inputs examples/valuation.json
```

4. For Claude skill installation, the standalone CLI launcher is `$HOME/.local/bin/fundtex` after `bash install.sh`; alternatively run `python3 -m fundtex_india.cli` from the cloned repo root.
5. Every result must show as-of date, sample count, data source URL/path, missing data, applicable assumptions, method, uncertainty and what would falsify the thesis.
6. For company-specific material news, verify exchange announcement or company investor-relations source, not RSS title alone. Official sources: [NSE](https://www.nseindia.com/), [BSE](https://www.bseindia.com/), [SEBI](https://www.sebi.gov.in/), [RBI](https://www.rbi.org.in/).
7. Always separate *facts* (linked primary filings, historical series) from *hypotheses* (growth, WACC, outlook), and clearly label synthetic examples.

## Analyst-grade output contract

Give: **Executive finding | Evidence and citations | Fundamental/market context | What changed | Upside/base/downside hypotheses | Risks & catalysts | Data freshness | Validation checklist.** Where research lacks verifiable evidence, say `NOT VERIFIED` rather than invent a figure.

## Guardrails

- No autonomous orders, no broker keys, no guaranteed returns. No trade execution supported by India engine.
- The legacy `trader-broker` skill is US-oriented; do not use it to send Indian trades. Institutional recommendations may require SEBI registration/compliance review.
- News headlines are unverified discovery leads, not facts. DCF sensitivities depend on explicitly disclosed human assumptions; a Monte Carlo draw is not a historical backtest or a forecast guarantee.
- Never distribute licensed exchange data without permission or upload client portfolios to third-party models without authorization.
