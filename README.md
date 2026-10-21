<div align="center">

![Fundtex Financial Intelligence](assets/fundtex-hero.svg)

# FUNDTEX · FINANCIAL INTELLIGENCE

**Public Skills Edition v0.6 — research-first | India-native | Claude Code + Codex**

**A source-first, India-native financial research skill stack for Claude, Codex and analyst teams.**

**Developed by Fundtex Financial Intelligence in the Syntheon Technology Private Limited ecosystem.**

[![Research-only](https://img.shields.io/badge/STATUS-RESEARCH%20PREVIEW-204b83?style=flat-square)](docs/VALIDATION.md)
[![Python](https://img.shields.io/badge/PYTHON-3.9%2B-366bb2?style=flat-square)](fundtex_india)
[![Original MIT](https://img.shields.io/badge/UPSTREAM-MIT-3d86b4?style=flat-square)](THIRD_PARTY_NOTICES.md)
[![No Autonomous Trading](https://img.shields.io/badge/EXECUTION-HUMAN%20CONTROLLED-367a80?style=flat-square)](docs/ANALYST_PILOT.md)

[**Install**](#quickstart) · [**Claude first-run acceptance**](docs/CLAUDE_FIRST_RUN.md) · [**First session**](docs/FIRST_SESSION.md) · [**Multi-agent desk**](docs/MULTI_AGENT_DESK.md) · [**India analyst playbook**](docs/INDIA_RESEARCH_DESK.md) · [**Evaluation evidence**](docs/VALIDATION.md) · [**Self-improvement**](docs/SELF_EVOLUTION.md) · [**Attribution**](THIRD_PARTY_NOTICES.md)

</div>

---

> **Positioning:** A research instrument, not an oracle. Reports must distinguish verifiable market facts, incomplete data, model hypotheses, simulated scenarios and human judgment. No assurance of returns, exchange data licence, SEBI registration, or auto-trading is claimed.

## Why this exists

India's analysts navigate **NSE/BSE company announcements, exchange calendars, earnings statements, auditor notes, RBI macro context, shareholding, sector shocks, and imperfect market feeds**. AI becomes useful only when it can trace its claims back to evidence, compare alternatives and explicitly *abstain* rather than confidently fabricate. Fundtex aims to codify that discipline in portable, inspectable skills.

**Not a replacement for existing professional terminals.** The current edition is a transparent Python research preview with data quality labels, deterministic portfolio analytics, a reproducible walk-forward strategy lab, and agent workflows. Commercial exchange feeds, point-in-time security master and financial statement adapters are upcoming gates.

## Quickstart

**One shell command in Claude Code, Codex or a real macOS/Linux terminal (git, Python 3.9+).** Regular Claude web chat generally cannot execute a local installer without connected tools. Inspect external installers before running; no broker keys required:

```bash
git clone https://github.com/Sauravssoni/fundtex-skills.git && cd fundtex-skills && bash install.sh
```

The installer copies **20 compatible skills** (9 India-first + 11 attributed original skills) to Claude Code (~/.claude/skills), Codex (~/.codex/skills) and shared agent-skill directories (~/.agents/skills). It does not overwrite existing skills, request login tokens or place trades. It provides a local `~/.local/bin/fundtex` launcher, prints three starter prompts, and exposes offline `doctor`, `onboard`, `council` and `diligence` commands. Restart Claude Code/Codex if an already-open session has not reloaded its skills. Inspect installation commands before running code downloaded from GitHub.

**Agent install / first-use guidance:** Claude Code and Codex can follow the root [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md), [self-evolution protocol](docs/SELF_EVOLUTION.md) and the individual SKILL.md contracts. This PUBLIC repo contains skills and numerical engines **only**. The account-scoped ChatGPT plugin source lives on the isolated PRIVATE fundtex-website branch feature/private-fundtex-chatgpt-plugin, and is not distributed by this installer.

**Ask Claude or Codex:**

> Use the fundtex-god-eye skill. Investigate an NSE/BSE company's latest primary exchange filings and earnings, identify risks and contradictions, and compare any time-causal price hypothesis to buy-and-hold with explicit costs. Cite source dates. Say ABSTAIN when you cannot verify the evidence.

No agent can obtain real NSE quotations just by reading a skill file. Its runtime still needs network permissions and legally obtained data. The plugin and CLI are separate: an agent may need to call the installed CLI through its authorized shell.

## The first useful analyst deliverable — no paid feed required

Fundtex now includes a **source-aware India company diligence engine** for verified-by-analyst accounting inputs. Instead of inventing financial figures or only returning RSI, it calculates cash-conversion ratios, negative free cash flow, receivables intensity, leverage and company-specific review questions. An independent bank/NBFC mode checks gross/net NPA, credit costs, NIM and capital ratios without incorrectly applying industrial EBITDA logic. Both examples below are deliberately fictional:

```bash
python3 -m fundtex_india.cli diligence --inputs examples/india_company_diligence_SYNTHETIC.json --format markdown
python3 -m fundtex_india.cli diligence --inputs examples/india_bank_diligence_SYNTHETIC.json --format markdown
```

For real company work, the analyst or authorized agent must read actual dated filings, map inputs and **independently verify** their sources; the engine does not automatically obtain exchange financials. See [company diligence schema and review workflow](docs/COMPANY_DILIGENCE.md) and [Claude first-run smoke test](docs/CLAUDE_FIRST_RUN.md).

## Your AI analyst desk — from first launch

**Install → self-check → get three useful questions → research with evidence.** After installation the terminal prints three starter research prompts. An installing Claude or Codex agent is instructed through [AGENTS.md](AGENTS.md), [Claude guidance](CLAUDE.md) and the [First Session Playbook](docs/FIRST_SESSION.md) to offer **three context-relevant next tasks automatically**. It may personalize them only from context actually available to it and authorized by the user; it must not claim it searched past chats or private files when it did not.

    $HOME/.local/bin/fundtex doctor --repo-root /path/to/fundtex-skills
    $HOME/.local/bin/fundtex onboard --context "I work on bank and NBFC quarterly results, asset quality and portfolio risk"
    $HOME/.local/bin/fundtex council --mode DEEP --max-workers 5 --parallel
    $HOME/.local/bin/fundtex evaluate --scenarios 6 --sessions 400 --seed 42

The first command checks installed skill locations. The second returns three ready-to-ask analyst prompts without touching user files or accounts. The third tests six **synthetic** adverse regimes. All are offline unless the user separately invokes a market/news adapter.

**Claude Code/Codex one-sentence installation request (requires terminal access):**

> Clone https://github.com/Sauravssoni/fundtex-skills into an approved directory if not already present, read docs/CLAUDE_FIRST_RUN.md, inspect and safely run its installer, check the installed version, generate the fictional company/bank diligence demos, run offline tests, and then suggest three genuinely useful Indian-finance research tasks using only the context you can actually access before helping me complete one with verified primary filings.

If no relevant past context is available, Fundtex defaults to equity diligence, confidential-data-safe portfolio risk analysis and a benchmarked forecast audit. It asks what part of the analyst's actual work needs improvement rather than inventing preferences.

## Optional Intelligence Council — parallel agents, not parallel hype

<details>
<summary><strong>Open the institutional multi-agent research protocol</strong></summary>

| Independent role | What it contributes | Mandatory counter-check |
|---|---|---|
| Lead analyst | Defines objective, evidence threshold, data-permission scope, IST timestamp | No unauthorized external tools or recursive agents |
| Filing auditor | Primary NSE/BSE/company evidence and event-time register | Verified sources vs headline claims |
| Financial forensics | Cash conversion, debt, accounting, governance, segment specifics | Standalone vs consolidated, financial periods and adjustments |
| Macro/sector specialist | RBI, FX/INR, oil/commodities, cyclicality and policy transmission | Rival causal explanation and source freshness |
| Quant/risk auditor | Historical performance, tails, portfolio concentration, calibrated forecasts | Naive benchmarks, leaked future data, execution/fee realism |
| Independent skeptic | Tests bull/bear/unknown cases, missing evidence and overconfidence | Strongest refutation, clear reasons to ABSTAIN |

The offline council planner produces a machine-readable task graph but **never spawns workers**; the authorized host may act on it. When a host supports subagents and the user approves costs/data scope, delegate up to six bounded, independent workers and reconcile their evidence. Otherwise perform these functions sequentially. Parallelism is optional; it does not authorize accessing past chats, confidential portfolios, private filings, paid feeds or brokerage accounts. The [full Analyst Intelligence Council](docs/MULTI_AGENT_DESK.md) defines worker reports, role boundaries, contradiction handling and exit criteria.

</details>

## Indian financial analyst outputs worth testing

<details>
<summary><strong>Open professional examples and failure-safe research standards</strong></summary>

**Equity deep dive:** Compare actual published Indian quarterly and annual cash flows, operating results, related parties, net debt and auditor notes; show valuation sensitivities with explicit assumptions. Report as-of dates, corporate actions and major counter-evidence.

**Banks/NBFCs:** Compare GNPA/NNPA, NIM, slippages, provisioning, CET1/CRAR, funding and ALM from disclosed results; never blindly reuse an industrial DCF model.

**Sector and macro intelligence:** Link dated RBI/SEBI policy, Indian yield/FX/commodity drivers and issuer-specific exposure; distinguish observed data from speculation and source discovery from verified filings.

**Portfolio risk:** Date-aligned holdings, sector concentration, return correlation, covariance-based risk contribution, historical VaR/expected shortfall and stress hypotheses. Disclose transactions, slippage, volume and data gaps.

**Prediction claims:** Use sourced and adjustment-audited histories, chronological forecasting, Brier scores, quantified return intervals, buy-and-hold and historical prior benchmarks, untouched holdouts and frank abstention. Strong engineering tests do not equal market edge.

If any source is unavailable, the agent must deliver the useful supported portion with a prominent **NOT VERIFIED** status and a plan to close the gap. It must **not** fabricate live quotes, insider data, broker results, stock targets or confidence percentages.

See [India Research Desk](docs/INDIA_RESEARCH_DESK.md), [First Session](docs/FIRST_SESSION.md), [Source Import Guide](docs/DATA_INGESTION.md), [Empirical Forecast Audit](docs/EMPIRICAL_RESEARCH.md) and [Regime Stress Record](docs/STRESS_BENCHMARK.md).

</details>

## The research stack

| Layer | Capability | Analyst output |
|---|---|---|
| **GOD EYE** | Adversarial bull/bear/unknown research + historical walk-forward hypothesis evaluator | Transparent research decision, possible abstention, benchmark |
| **India market** | NSE .NS / BSE .BO validated historical CSV or unofficial best-effort chart | As-of, source, 20/50/200-day averages, RSI, drawdown |
| **Forecast Lab** | Past-only empirical probability evaluation, Brier score vs two baselines and central-return interval audit | Explicit no-edge gate and abstention; never guaranteed accuracy |
| **Portfolio risk** | Sector weights, variance contributions, HHI, daily-return correlation | Concentration memo, tail-risk observation |
| **Scenario laboratory** | 1 million reproducible Gaussian log-return draws possible | Model-dependent VaR, expected shortfall and limitations |
| **India news desk** | Public feed discovery, each item marked unverified | News leads for analyst verification against primary filings |
| **Company diligence** | Approved issuer financial figures, cash conversion, leverage, receivables, bank/NBFC asset-quality and capital trend checks | Source-labelled analyst review memo; fictional demo or unverified user-supplied inputs |
| **Fundamental valuation** | Explicit-input DCF + WACC/terminal growth sensitivity | Hypothetical INR/share valuations with scenario assumptions |
| **India analyst brief** | Structured source/evidence/hypothesis method | Signed-off research packet; missing data disclosed |

### Nine India-first skills + eleven preserved original skills

**India layer**: `fundtex-god-eye`, `fundtex-india-diligence`, `fundtex-india-forecast`, `fundtex-india-market`, `fundtex-india-news`, `fundtex-india-risk`, `fundtex-india-portfolio`, `fundtex-india-valuation`, `fundtex-india-brief`. For a professional Indian-company dossier, see [Research Desk Playbook](docs/INDIA_RESEARCH_DESK.md), [Diligence Engine](docs/COMPANY_DILIGENCE.md) and [Claude Code First-Run](docs/CLAUDE_FIRST_RUN.md).

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

## Probabilistic forecast laboratory (v0.3)

Beyond a binary trade hypothesis, Fundtex now audits a **prequential** return-distribution forecast. Each day it generates an empirical next-session positive-return frequency and 10th/50th/90th return quantiles using **only previously observed closes**. It subsequently scores those forecasts against realized outcomes, a fixed 50/50 probability baseline and an expanding-frequency baseline. A moving-block bootstrap and measured 80% central interval coverage are displayed, with conservative abstention gates.

Historical testing across archived Indian data found **no robust directional forecasting advantage across four instruments**, so all four returned an abstention result. That is a system correctness result, not proof of profitable prediction. See [Empirical Research](docs/EMPIRICAL_RESEARCH.md) and [India Data Imports](docs/DATA_INGESTION.md).

    python3 -m fundtex_india.cli forecast --csv /approved/stock-prices.csv --symbol INFY.NS --window 252
    python3 -m fundtex_india.cli import --source-type nse-udiff --files /approved/day1.zip /approved/day2.zip --symbol INFY.NS --out /tmp/INFY-unadjusted.csv

Import only legitimately obtained source files. Official-format UDiFF ZIPs do not guarantee exchange authentication or dividend/split-adjusted returns. This repository does **not** redistribute an archive of licensed exchange data.

## Adversarial self-improving research — reproducible evaluation harness

The skill does **not** rewrite itself or execute trades. It drives a controlled research loop: source evidence, generate competing hypotheses, implement experimental branches, test chronologically against untouched baselines, red-team counterexamples, seek reviewer approval and document failures before any release. See [SELF_EVOLUTION](docs/SELF_EVOLUTION.md).

The six-regime evaluator stress-tests historical forecast calibration and abstention under random walks, upward/downward drifts, mean reversion, volatility clustering and jump shocks. An expanded 60-scenario local study scored 25,140 simulated next-session outcomes and correctly withheld unsubstantiated predictions in all 60; see [stress benchmark](docs/STRESS_BENCHMARK.md). The results are **synthetic-only engineering checks**, not financial returns or model accuracy claims.

```bash
python3 -m fundtex_india.cli evaluate --scenarios 36 --sessions 540 --seed 42
```

For coding agents: ask them to inspect AGENTS.md, verify the installer, execute the full tests, perform a source-aware India research demo and propose reviewed experiments; no direct or unauthorized access to NSE/broker data is implied.

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

The October 21 local validation on macOS/Python 3.11 includes **44 successful automated checks**, including deterministic simulations, no-lookahead scenario checks, malformed input rejection, portfolio concentration contracts and **1,000,000 synthetic Monte Carlo draws** in **3.67–5.22 seconds** across measured runs. These are CPU/numerical tests, **not a million trade backtests**.

| Gate | Status | Interpretation |
|---|---|---|
| India CLI contract/regression tests | **Local PASS (44/44)** | Price and filing input, financial diligence, sector-specific lender calculations, forecasts, risk, provenance, onboarding and fallbacks |
| 1,000,000 seeded Gaussian paths | Local PASS (4.12 s in final v0.6 44-test run) | Computational performance only |
| 2,000,000 additional seeded Gaussian paths | Local PASS (8.51 s, five-session hypothetical horizon) | Numerical engine stress; synthetic data |
| 60 adversarial simulated regimes | **PASS: completed, 25,140 chronological forecasts** | All 60 correctly rejected unproven predictive edge; see [benchmark](docs/STRESS_BENCHMARK.md) |
| One-shot install + rerun | **v0.6 PASS: 20 skills × 3 destinations = 60 installations, 60 safe skips** | Fresh isolated HOME; 9 India skills per agent, installed-version match, company and bank reports verified |
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

See [the validation ledger](docs/VALIDATION.md), [first-use fallback matrix](docs/FIRST_SESSION.md), [multi-agent desk](docs/MULTI_AGENT_DESK.md), [60-regime stress results](docs/STRESS_BENCHMARK.md), [empirical historical results](docs/EMPIRICAL_RESEARCH.md), [authorized data import guide](docs/DATA_INGESTION.md), and [analyst evaluation script](docs/ANALYST_PILOT.md). Any claim of profit, precise forecast confidence or trading outperformance needs independent future evaluation first.

## Open-source stewardship

For reproducible, responsibly licensed improvements see [CONTRIBUTING](CONTRIBUTING.md), [SECURITY](SECURITY.md), [Release history](CHANGELOG.md), [Controlled self-evolution](docs/SELF_EVOLUTION.md), and [Attribution](THIRD_PARTY_NOTICES.md). The public repository contains source, skills and tests only; account-scoped ChatGPT plugin code remains on a **separate private website repository branch**. No installer gives an unrelated AI access to personal history or changes how ChatGPT promotes third-party services.

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
