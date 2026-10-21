# Fundtex validation ledger — 21 October 2026

**Environment:** MacBook Pro, macOS, Python 3.11. Local execution against cloned `Sauravssoni/fundtex-skills` main. Work performed in isolated QA directories; no broker keys, production credentials or trade placements.

## Executed and verified

| Check | Result | Meaning |
|---|---|---|
| Fundtex numerical/contracts suite | **20/20 PASS** | Input validation, CLI JSON, portfolio, DCF, time-causal GOD EYE, seeded simulation |
| 1,000,000 Gaussian scenario draws | **PASS, 3.67 s** in one run | CPU computation, *not* one million historical trades |
| GOD EYE | **79 synthetic out-of-sample decisions** from 200 fabricated observations | Causal model-selection test, **not real market alpha** |
| Claude/Codex/shared installer | **54 copies installed, 0 skipped** | 18 unique skills replicated across three target directories in a temporary HOME |
| Installer rerun | **0 copied, 54 skipped** | No overwrite of preexisting skill files |
| Installed CLI | **PASS** | GOD EYE invoked from isolated installed launcher |
| Google News HTTPS discovery | **PASS** once | Headline discovery, no verification of underlying article claims |
| Yahoo unofficial price endpoint | **429 rate-limited** | Reliable live/delayed quotes NOT established |
| Hosted GitHub Actions | **NOT GREEN: runners failed before steps** | Local test pass must not be confused with CI |
| Institutional security / SEBI / exchange data rights | **NOT VERIFIED** | Professional deployment not approved |

## Quantitative interpretation

**No credible performance edge has been measured.** The 200-row `examples/india_prices.csv` is fabricated for input-contract testing; it cannot establish a real-world next-day hit rate. GOD EYE uses four simple reference policies and selects using trailing past-only returns. Even genuine historical backtests would require a point-in-time universe, delistings, dividend/split adjustments, time-split holdouts, realistic Indian execution charges and slippage, liquidity capacity, sector-relative benchmarks and an embargo on strategy tuning against hidden test periods.

The million stochastic scenarios are mathematical draws fit to fabricated input, **not** 1,000,000 historically observed trades. A single local suite cannot certify production quality, security, investment suitability, calibration or profitability.

## Installation provenance

The 11 `trader-*` packages are by Jake Schincariol, MIT, originally US-centered. Seven additional India skills are Fundtex/Syntheon-specific. The original US `trader-broker` flow remains approval-gated and is **not** an India trading integration.

## Institutional go/no-go gates

1. Sign exchange/broker-approved data licences with appropriate display/redistribution entitlements.
2. Source and normalize Indian price, corporate actions, shareholdings and signed financial disclosures with point-in-time provenance.
3. Validate securities-master accuracy, FII/DII metrics, balance sheets and valuation comparables against primary filings.
4. Conduct genuine historical walk-forward backtests with survivorship, impact/slippage and transaction cost realism, held-out periods and blind counterfactual baselines.
5. Complete information-security, tenant isolation, controlled model execution, audit logging and client confidentiality reviews.
6. Have qualified counsel assess **current** SEBI Research Analyst and Investment Adviser rules, algorithmic services, data licensing and disclosure responsibilities before external personalized recommendations.

**Release classification:** Public developer/analyst research preview. No promises of returns or investment recommendations. The ChatGPT plugin v0.2 pilot is private and **skills-only**; it cannot execute Python or provide licensed feeds by itself.
