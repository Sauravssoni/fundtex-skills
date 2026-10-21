# FUNDTEX FINANCIAL INTELLIGENCE 🇮🇳

**Fundtex Financial Intelligence** — a fintech financial-research initiative in the **Syntheon Technology Private Limited** ecosystem.

India-first investment-research skill pack. Keeps all **11 original MIT-licensed trader-skill modules** from [Jake Schincariol](https://github.com/Jakeschincariol/trader-skill) and adds **6 Fundtex India Claude skills** and a reproducible Python research engine for NSE/BSE equity workflows.

**Positioning:** Source-first, analyst-reviewed financial intelligence. Fundtex is not presented as a registered SEBI investment adviser/research analyst, licensed exchange data vendor, brokerage, or proven alpha engine.

## One-shot setup

macOS or Linux, git + Python 3.9+, no Python package dependencies:

```bash
git clone https://github.com/Sauravssoni/fundtex-skills.git && cd fundtex-skills && bash install.sh
```

Installs non-conflicting skill folders under `~/.claude/skills` and the read-only India CLI at `$HOME/.local/bin/fundtex`. Existing folders/binaries are skipped, not overwritten. Restart Claude Code and invoke the Fundtex India skills.

**Claude Code plugin alternative:**

```text
/plugin marketplace add Sauravssoni/fundtex-skills
/plugin install fundtex-intelligence@fundtex
```

## India analyst workflows

```bash
python3 -m fundtex_india.cli analyze --csv examples/india_prices.csv --symbol RELIANCE.NS
python3 -m fundtex_india.cli simulate --csv examples/india_prices.csv --symbol RELIANCE.NS --paths 1000000 --horizon 1 --seed 42
python3 -m fundtex_india.cli value --inputs examples/valuation.json
python3 -m fundtex_india.cli news --query 'Infosys NSE earnings'
python3 -m fundtex_india.cli brief --csv examples/india_prices.csv --symbol RELIANCE.NS
python3 -m fundtex_india.cli portfolio --prices examples/portfolio_prices.csv --holdings examples/holdings.csv
python3 -m fundtex_india.cli analyze --live --symbol INFY.NS
```

`--live` uses an **unofficial, best-effort Yahoo historical chart**, *not* a live NSE/BSE exchange-grade quote or data licence; it may be delayed, rate-limited, blocked or inaccurate. Only use it where terms allow. Prefer institution-approved historical exports with `date,symbol,close` or `timestamp,symbol,close`; confirm adjusted-close treatment.

**The included example price series and valuation assumptions are deliberately synthetic.** They must never be cited as actual Reliance market history, live prices, company reported numbers, or predictive performance.

## What it does

| Component | Function | Evidence status |
|---|---|---|
| 11 retained `trader-*` skills | US 13F copying, US SEC earnings, Congress filings, US news, budgets, screener, risk gating, broker ticket preparation, tax lots, price alerts and rebalancing | Original US-only data sources and assumptions preserved; see `docs/UPSTREAM_README.md` |
| `fundtex-india-market` | Dated India symbol and closing-price analysis | Validated imported CSV or unofficial Yahoo historical chart |
| `fundtex-india-risk` | Drawdown, return volatility, Sharpe approximation, RSI, historical 95% VaR/expected shortfall | Based on historical input; no guarantee |
| `fundtex-india-news` | Indian market news lead discovery | Google News RSS: `UNVERIFIED_HEADLINE_DISCOVERY`; verify primary filings |
| `fundtex-india-valuation` | DCF scenario and WACC/terminal-growth sensitivity | Explicit user hypothesis, **not market data** |
| `fundtex-india-portfolio` | Multi-stock date-aligned sector exposure, covariance, portfolio risk and risk contribution | User-supplied CSV series, daily-rebalanced hypothetical returns |
| `fundtex-india-brief` | Sourced, analyst-reviewed summary template | Source quality surfaced in report |
| `simulate` | 1M seeded Gaussian log-return scenario draws | Model-scenario test; **not** 1M historical trades or validated strategy alpha |

## Verification

```bash
python3 -m unittest discover -s tests -p 'test_fundtex*.py' -v
RUN_MILLION_TEST=1 python3 -m unittest -v tests.test_fundtex_million
python3 -m compileall -q fundtex_india
```

The test suite exercises CSV validation, provenance labels, risk formulas, failure behavior, seeded reproducibility, DCF checks and a computational million-path gate. The latter tests numerical execution only. CI status must be checked before reporting a pass; GitHub Actions jobs can fail to start when an account has runner/billing restrictions.

## India analyst-review and compliance contract

All results should include source, link/filename, as-of date, samples, methodology, limitations, alternatives, sensitivity and contradictory evidence. Verify corporate disclosures with [NSE](https://www.nseindia.com/), [BSE](https://www.bseindia.com/), company investor-relations material, [SEBI](https://www.sebi.gov.in/) and [RBI](https://www.rbi.org.in/). Institutional research, client recommendations, redistribution of exchange data, and AI processing of confidential client information can require extra regulatory, data-licensing and infosec controls.

**Safety:** India CLI is read-only and has **no brokerage integration**. Do not use the original US broker pathway to execute Indian orders. No autonomous trading, derivatives leverage, assured returns or production security certification.

**Licensing:** Original `trader-*` code is MIT by Jake Schincariol; see original `LICENSE` and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Fundtex additions are separate. No endorsement by upstream project.

## Next institutional gates

Licensed NSE/BSE pricing and corporate actions; financial-statement ingestion with filing evidence; INR portfolio/sector factor risk; genuine historical walk-forward backtests with delistings, costs and survivorship-bias controls; versioned models; access control, audit trails and security review; explicit SEBI/legal counsel review for regulated external advisory use.
