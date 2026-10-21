<div align="center">

![Fundtex Financial Intelligence](assets/fundtex-hero.svg)

# FUNDTEX · FINANCIAL INTELLIGENCE

**A source-first, India-native financial research skill stack for Claude, Codex and analyst teams.**

**Developed by Fundtex Financial Intelligence in the Syntheon Technology Private Limited ecosystem.**

[![Research-only](https://img.shields.io/badge/STATUS-RESEARCH%20PREVIEW-204b83?style=flat-square)](docs/VALIDATION.md)
[![Python](https://img.shields.io/badge/PYTHON-3.9%2B-366bb2?style=flat-square)](fundtex_india)
[![Original MIT](https://img.shields.io/badge/UPSTREAM-MIT-3d86b4?style=flat-square)](THIRD_PARTY_NOTICES.md)
[![No Autonomous Trading](https://img.shields.io/badge/EXECUTION-HUMAN%20CONTROLLED-367a80?style=flat-square)](docs/ANALYST_PILOT.md)

[**Product page**](https://fundedtex.com/financial-skills) · [**Quickstart**](#quickstart) · [**GOD EYE**](#god-eye--time-causal-research) · [**Analyst trial**](docs/ANALYST_PILOT.md) · [**Validation**](docs/VALIDATION.md) · [**Source attribution**](THIRD_PARTY_NOTICES.md)

</div>

---

> **Positioning:** A research instrument, not an oracle. Reports must distinguish verifiable market facts, incomplete data, model hypotheses, simulated scenarios and human judgment. No assurance of returns, exchange data licence, SEBI registration, or auto-trading is claimed.

## Why this exists

India's analysts navigate **NSE/BSE company announcements, exchange calendars, earnings statements, auditor notes, RBI macro context, shareholding, sector shocks, and imperfect market feeds**. AI becomes useful only when it can trace its claims back to evidence, compare alternatives and explicitly *abstain* rather than confidently fabricate. Fundtex aims to codify that discipline in portable, inspectable skills.

**Not a replacement for existing professional terminals.** The current edition is a transparent Python research preview with data quality labels, deterministic portfolio analytics, a reproducible walk-forward strategy lab, and agent workflows. Commercial exchange feeds, point-in-time security master and financial statement adapters are upcoming gates.

## Quickstart

**One shell command for macOS/Linux (git, Python 3.9+):**

```bash
git clone https://github.com/Sauravssoni/fundtex-skills.git && cd fundtex-skills && bash install.sh
```

The reviewed installer copies skills to Claude Code (~/.claude/skills), Codex (~/.codex/skills) and shared agent-skill directories (~/.agents/skills). It does not overwrite existing skills, request login tokens or place trades. It provides a local `~/.local/bin/fundtex` launcher. Inspect installation commands before running code downloaded from GitHub.

**Claude Code marketplace alternative:**

```text
/plugin marketplace add Sauravssoni/fundtex-skills
/plugin install fundtex-intelligence@fundtex
```

**Ask Claude or Codex:**

> Use the fundtex-god-eye skill. Investigate an NSE/BSE company's latest primary exchange filings and earnings, identify risks and contradictions, and compare any time-causal price hypothesis to buy-and-hold with explicit costs. Cite source dates. Say ABSTAIN when you cannot verify the evidence.

No agent can obtain real NSE quotations just by reading a skill file. Its runtime still needs network permissions and legally obtained data. The plugin and CLI are separate: an agent may need to call the installed CLI through its authorized shell.

## The research stack

| Layer | Capability | Analyst output |
|---|---|---|
| **GOD EYE** | Adversarial bull/bear/unknown research + historical walk-forward hypothesis evaluator | Transparent research decision, possible abstention, benchmark |
| **India market** | NSE .NS / BSE .BO validated historical CSV or unofficial best-effort chart | As-of, source, 20/50/200-day averages, RSI, drawdown |
| **Portfolio risk** | Sector weights, variance contributions, HHI, daily-return correlation | Concentration memo, tail-risk observation |
| **Scenario laboratory** | 1 million reproducible Gaussian log-return draws possible | Model-dependent VaR, expected shortfall and limitations |
| **India news desk** | Public feed discovery, each item marked unverified | News leads for analyst verification against primary filings |
| **Fundamental valuation** | Explicit-input DCF + WACC/terminal growth sensitivity | Hypothetical INR/share valuations with scenario assumptions |
| **India analyst brief** | Structured source/evidence/hypothesis method | Signed-off research packet; missing data disclosed |

### Seven India-first skills + eleven preserved original skills

**India layer**: `fundtex-god-eye`, `fundtex-india-market`, `fundtex-india-news`, `fundtex-india-risk`, `fundtex-india-portfolio`, `fundtex-india-valuation`, `fundtex-india-brief`.

**Preserved 11 original US modules** (by Jake Schincariol): `trader-copycat`, `trader-news`, `trader-budget`, `trader-pelosi`, `trader-analyst`, `trader-screener`, `trader-risk`, `trader-broker`, `trader-tax`, `trader-alerts`, `trader-rebalance`. Their source methods are US-centric (SEC/NYSE/US tax/congress); **they are not automatically an Indian trading/tax connector**. The original brokerage component prepares approval-gated *US* tickets; the Fundtex India engine is read-only.

## GOD EYE — time-causal research

```text
                 FUNDAMENTALS / EARNINGS  ──┐
       NSE & BSE DISCLOSURES / EVENTS  ─────┼─► Evidence ledger
         RBI / SEBI / MACRO CONTEXT    ─────┤   timestamps + counterclaims
        APPROVED HISTORICAL PRICES    ──────┘
                                                 │
                                Bull ◀── Thesis ──▶ Bear
                                                 │
                        Prior-only walk-forward + costs
                                                 │
                     Buy & hold baseline / cash benchmark
                                                 │
                              HUMAN REVIEW · ABSTAIN
```

The current price-hypothesis lab compares four **simple transparent** strategies (momentum20, reversion5, trend20x60, breakout20) against cost-adjusted buy-and-hold. Each day's candidate is selected using **only prices and realized returns available by that decision close**. If no method scored positively on its trailing window, it enters a hypothetical cash/abstain position. This is **not evidence of live predictive accuracy**, and the evaluation does not yet have an independently constructed point-in-time universe, full Indian fee model, delisting adjustment or live-forward performance record.

```bash
python3 -m fundtex_india.cli godeye --csv examples/india_prices.csv --symbol RELIANCE.NS
```

**Example inputs are synthetic and do not represent historical Reliance pricing.** Use approved adjustment-corrected exports for real research.

## Analyst commands

```bash
# Evidence-labelled historical volatility, RSI, drawdown and tail risk
python3 -m fundtex_india.cli analyze --csv examples/india_prices.csv --symbol RELIANCE.NS

# Sector / covariance contribution / correlation / concentration
python3 -m fundtex_india.cli portfolio --prices examples/portfolio_prices.csv --holdings examples/holdings.csv

# Strict past-only research-policy selection + OOS comparison
python3 -m fundtex_india.cli godeye --csv examples/india_prices.csv --symbol RELIANCE.NS --min-train 120 --train-lookback 60 --cost-bps 12

# Explicit assumption valuation in INR/share
python3 -m fundtex_india.cli value --inputs examples/valuation.json

# Reproducible synthetic distribution scenarios (NOT historical backtests)
python3 -m fundtex_india.cli simulate --csv examples/india_prices.csv --symbol RELIANCE.NS --paths 1000000 --seed 42

# Discover unverified headline leads (no assertion without opening a source)
python3 -m fundtex_india.cli news --query "Infosys NSE earnings"
```

The `--live` option accesses a **best-effort unofficial Yahoo historical chart**, not a real-time exchange-certified NSE/BSE feed. It can rate-limit with HTTP 429 and has not demonstrated reliable availability for professional use.

## What has actually been tested?

The October 21 local validation on macOS/Python 3.11 includes **20 successful automated checks**, including deterministic simulations, no-lookahead scenario checks, malformed input rejection, portfolio concentration contracts and **1,000,000 synthetic Monte Carlo draws** in approximately **3.67 seconds** in that specific run. These are CPU/numerical tests, **not a million trade backtests**.

| Gate | Status | Interpretation |
|---|---|---|
| India CLI contract/regression tests | Local PASS (20/20) | Basic known contracts in a single environment |
| 1,000,000 seeded Gaussian paths | Local PASS | Computational performance only |
| One-shot install + rerun | Tested earlier (17 skills); expanded multi-agent install requires new regression | Snapshot copy; no overwrite |
| Google News discovery | Live tested once | Unverified leads; independent verification required |
| Yahoo price fetch on test host | HTTP 429 | Not dependable live-market validation |
| Fully licensed NSE/BSE prices & filings | NOT DONE | Institution feed integration needed |
| Out-of-sample prediction on real PIT universe | NOT DONE | **No proven investment edge** |
| Production GitHub CI | NOT GREEN | Hosted runner failed before any tests started |

Reproduce:

```bash
python3 -m unittest discover -s tests -p "test_fundtex*.py" -v
RUN_MILLION_TEST=1 python3 -m unittest -v tests.test_fundtex_million
```

See [the evidence ledger](docs/VALIDATION.md) and [an analyst UAT script](docs/ANALYST_PILOT.md). Any claim of profit, precise forecast confidence or trading outperformance needs independent future evaluation first.

## Legal, privacy and data governance

- **NSE data:** usage, redistribution and display are governed by [NSE market-data policy](https://www.nseindia.com/static/market-data/nse-data-policy). Access through this repo does not grant redistribution rights.
- **SEBI:** review the most current [Research Analyst rules](https://www.sebi.gov.in/) before providing investment research services, algorithmic recommendation or external client advice, including AI disclosures, registration and security responsibilities.
- **Data:** client holdings, portfolio models and documents must not be sent to outside AI tools without the owning institution's consent and security review.
- **Trading:** no autonomous India live brokerage path, no margin/F&O engine, no performance guarantee or suitability assessment.

## Roadmap: what earns the next level

Licensed NSE/BSE feed contracts and corporate-action adjustment; primary filings/financial-statement parser with citations; Indian charges/taxes/settlement rules reviewed by specialists; point-in-time historical backtest with survivorship, liquidity and slippage; blind holdouts and rolling forward-paper evaluation; risk-constrained portfolio optimization and institution-grade approval/audit/tenant isolation; a real-data MCP service for a full ChatGPT integration.

**Open source does not mean unlicensed datasets or verified predictions.** Contributions are welcome with reproducible tests, honest baselines, data provenance and disclosure of model limitations.

---

<div align="center">

**Fundtex Financial Intelligence** · **Syntheon Technology Private Limited**

Original `trader-*` work © 2026 Jake Schincariol, MIT. Attribution preserved in [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Separate Fundtex India additions are not affiliated with or endorsed by the upstream author.

</div>
