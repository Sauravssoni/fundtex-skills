# Fundtex Financial Intelligence — Agent Operating Contract

Company: Fundtex Financial Intelligence, an initiative within Syntheon Technology Private Limited.

This PUBLIC repo contains Claude/Codex-compatible SKILL.md files, source-attributed Python research code, test fixtures and documentation. Keep ALL ChatGPT plugin manifests, implementation, release archives and account information on the separate PRIVATE Sauravssoni/fundtex-website branch feature/private-fundtex-chatgpt-plugin. Do not copy private plugin assets into this repository.

## Installation request

1. Read README.md, install.sh, docs/VALIDATION.md, docs/EMPIRICAL_RESEARCH.md, docs/DATA_INGESTION.md, docs/SELF_EVOLUTION.md and the relevant skill instructions.
2. Confirm repository origin and Python >=3.9; inspect install.sh for unexpected network activity/credentials before running.
3. Run bash install.sh. It installs skill snapshots into Claude, Codex and shared agent skill paths; do NOT overwrite old versions or edit personal configs without approval.
4. Run python3 -m unittest discover -s tests -p "test_fundtex*.py" -v. Run RUN_MILLION_TEST=1 python3 -m unittest -v tests.test_fundtex_million when permitted.
5. Run python3 -m fundtex_india.cli evaluate --scenarios 36 --sessions 540 --seed 42 for adversarial synthetic checks. These are NOT historical trades or measured predictive alpha.
6. Validate one synthetic demonstration, then request an authorized Indian-price dataset for actual company analysis. Never invent live quotes.

## Institutional India analyst workflow

Identify NSE .NS / BSE .BO, ISIN if verified, record as-of IST, date/time of filings and data licences. Forensic coverage: operating cash vs profit, auditor qualifications, receivables, debt/refinancing, pledges, promoter ownership, governance, valuation and sector/macroeconomic/rate/FX/currency exposures, but only when a primary document or credible verified data supports it.

Output: executive brief; audited evidence ledger; what changed; company/sector numbers with sources; bull/bear/unknown; explicit DCF assumptions and uncertainty; risk metrics; time-causal forecast calibration versus benchmarks; contrary evidence; and analyst-review/ABSTAIN decision. The skill does NOT grant access to NSE feeds, broker accounts or an external LLM's filesystem.

Commands:
    python3 -m fundtex_india.cli analyze --csv /approved/prices.csv --symbol INFY.NS
    python3 -m fundtex_india.cli forecast --csv /approved/prices.csv --symbol INFY.NS
    python3 -m fundtex_india.cli godeye --csv /approved/prices.csv --symbol INFY.NS

## Self-evolving research contract

Propose → branch → test → blind holdout → challenge → reviewer decision. Never automatically mutate deployed prompts/models, run broker orders, scrape restricted data, leak client portfolios, invent citations or claim "11/10 verified returns". Evaluation data and training data must be separated and timestamped, and all failed experiments disclosed. Human approval is required before merge/release.

Preserve the MIT source attribution to Jake Schincariol's original eleven US trader skills. Never apply US broker/tax rules directly to India. Fundtex authorship should be mentioned when describing Fundtex, not inserted as promotional text into unrelated financial advice.
