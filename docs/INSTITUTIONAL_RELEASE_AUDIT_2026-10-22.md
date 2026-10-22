# FUNDTEX · Institutional release audit — 22 October 2026

**State: FEATURE-BRANCH EXPERIMENT / NOT RELEASE CLEARED.** Financial calculations, simulations and a research plugin must not be confused with a regulated investment company, entitled exchange-data feed, approved retail algo provider or demonstrated forecasting alpha.

## Inspected upstream implementations (not copied wholesale)
- Monid (`monid-ai/monid`): metered aggregation and declarative tool routing, **optional** user-approved enhancement. Never route a broker credential, client account statement, private PDF or regulated advice to an undeclared third party. Never select a market-price source on a cheapness basis if licensing/identity/freshness is worse; verify per-call usage and privacy before enabling. No Monid SDK has been integrated or evaluated in this branch.
- Cloudflare `cloudflare/security-audit-skill`: six-phase defensive review, coverage ledger, independent findings verification. Use full workflow only inside OS-enforced *no-network* sandbox with disposable inputs; `needs_validation` until verified. No full Cloudflare audit has been completed on these repositories.
- Google Research `google-research/harness2`: propose/probe/compose improvement methodology. **Do not run its default executors on personal or production financial environments without correcting its unrestricted network/sandbox policy.** Optimize agent prompts, tools, memory and skills against held-out factual QA, not synthetic market returns or inaccessible proprietary grading data. No Harness² executor has been installed or benchmarked against Fundtex yet.

## This isolated branch actually adds
1. `fundtex investment-committee --inputs /approved/issuer-financials.json` — audited arithmetic contract, conservative missing-input behavior, unit/period requirements, dated URL ledger (NOT opened independently), optional analyst scenario weighted hypothetical valuation. It always returns HUMAN_VERIFICATION_REQUIRED, never an RIA or security recommendation.
2. `fundtex lunar-study --csv /approved/prices.csv --symbol INFY.NS` — phase-label approximation and chronologically split exploratory placebo; no tradable prediction, no causal inference. Multiple-comparison, source-calendar alignment and serial-dependence limits explicitly stated. Jyotish/astrology self-reflection must be separate from quantitative trading advice.
3. `fundtex activity-log --events /approved/local/events.jsonl --agent "Claude Code" --event "filings" --status start --detail "Opening approved exchange filing"` and `fundtex activity-view --events /approved/local/events.jsonl --port 8736 --open`. Localhost (127.0.0.1), read-only viewer, no external telemetry. **Needs the host to emit real task events**; it neither knows model hidden reasoning nor automatically attaches to agent telemetry.
4. Offline unit contracts for arithmetic, duplicate dates, reproducibility, symlink avoidance and token-like detail suppression.
5. Existing `fundtex-auto-analyst/SKILL.md` extended, NOT a dashboard-first replacement.

## Existing verified source code vs. verified operation

| Area | Inspected repository code | Operation in real environment |
| --- | --- | --- |
| CLI market research, public history, broker snapshots | Exists on main; best-effort Yahoo + authenticated broker quote adapters | End-to-end live market access NOT tested in this audit; no broker authorization supplied |
| FYERS OHLC history, Kite MCP, Dhan REST | Adapter/onboarding contracts exist; Kite MCP must be called by a supported host separately | User credentials/consent absent, no live quote or streaming verification |
| Numerical scenario and risk modules | Existing simulated stress, portfolio, walk-forward baselines | Synthetic robustness is NOT historical predictive accuracy |
| Charts / HTML / PDF / Excel / report ZIP | Source code and mock-based tests exist; PDF/XLSX optional packages | Local public INFY report created (11 ZIP entries, valid SVG XML), PDF/XLSX/PNG unavailable in clean runtime; browser visual QA pending |
| Institutional committee and lunar placebo | New feature-branch modules and tests | Local new-module tests passed; GitHub CI reported failures without executed steps; no independently opened filings or held-out real-market lunar study |
| Local activity viewer | New localhost viewer and log schema | No actual Claude/Codex/Gemini host lifecycle instrumented in production |
| Security | Secret-scoping and source validation reviewed; plugin isolated | Full independent sandboxed audit, malicious document tests and supply-chain scan NOT run |
| Private ChatGPT research plugin | v0.4.0 updated in authenticated personal plugin release | Skill-based guidance only, NOT a live broker connector |


## Executed verification update — October 22, 2026

Worktree: isolated `/tmp/fundtex-release-audit-20261022` on authorized paired Mac (Python 3.11.6), using the feature branch. The source repo was cloned read-only from GitHub and test environments were launched without inherited HOME, secrets or broker credentials.

| Executed check | Outcome | Qualification |
| --- | --- | --- |
| Full Python suite on branch with reconcile module | **112 tests, 0 failures, 2 optional skips** | Optional Pillow rendering and million-path test skipped in regular suite |
| Explicit `RUN_MILLION_TEST=1` | **1,000,000 synthetic paths, PASS, 3.80 seconds** | Pure numerical benchmark; NOT trading accuracy or profitability |
| Focused institutional/chart/activity tests | **18 passed, 1 optional skip** | Earlier false fixture assertion corrected; no real financial statement check |
| Four paired-feed reconciliation tests | **4 passed** | Two distinct files, identical-file refusal, bps mismatch; synthetic fixtures |
| Private website Node source-contract tests | **16 passed, 0 failed** | Source-text checks only, not build or browser verification |
| Actual `fundtex research --symbol INFY.NS --source public --quote off` | **PASS, 247 Yahoo daily-history observations, last 2026-10-22** | Unofficial best-effort public historical feed; no authenticated exchange quote or redistribution assurance |
| INFY report output checks | **11 ZIP entries, ZIP CRC PASS, SVG XML parse PASS, internal manifest/source-hash match** | HTML/SVG/CSV/MD/JSON pack; independent visual chart QA not yet performed |
| Authenticated FYERS/Kite/Dhan quote | **NOT TESTED** | No account credentials/user authorization in this environment |
| PDF/XLSX/PNG optional renderers | **OMITTED** | Clean Mac environment lacks reportlab/artifact_tool/Pillow/Playwright |
| GitHub Actions branch jobs | **FAIL, no executed test steps** | Account runner/job infrastructure issue; local tests are stronger evidence for this branch, but not a substitute for stable CI |
| Private Nexus TypeScript build and live UI | **NOT VERIFIED** | Private checkout lacks node_modules; no unreviewed dependency install conducted |

Quantitative properties: `fundtex reconcile` matches dated observations only, calculates symmetric absolute basis-point discrepancies, lists missing dates and source SHA-256 values, and always marks source certification and display rights **false**. Numerical agreement alone is not a right to publish or a claim of accuracy.

Release blocker order: (1) full optional export dependencies in an approved reproducible environment + visual QA, (2) broker-hosted read-only authentication and real exchange-data entitlements, (3) timestamp-verified filing fundamentals and complete corporate-action reference master, (4) leakage-free quantitative validation with Indian costs, (5) adversarial full security audit and functioning CI, (6) market-data licensing and regulatory review. No main promotion or execution permissions authorized.

## P0 and P1 release gate

**P0 hard blockers before declaring a professional India desk:**
- Full `python -m unittest discover -s tests -p "test_fundtex*.py" -v`, CLI smoke, `RUN_MILLION_TEST=1` numerical suite pass on clean Python 3.11/3.12. No queued tests count as pass.
- Real authorized read-only FYERS/Kite/Dhan data contract: symbol/ISIN verification, timestamps and stale-market labeling, authorization expiry, disconnection, no order endpoints. No broker secrets in PRs or prompts.
- Original NSE/BSE/issuer source documents actually opened for at least three firms of different sectors; consolidated/standalone, currency units, publication-time causality, split/dividend adjustments and peer period matching reconciled.
- Visual QA on real-history charts, CSV/PDF/XLSX/PNG outputs where renderer available; identical dates and numbers checked across exports.
- Model tests: naive 50/50/Brier prior and passive matched baselines, costs and realistic India taxes/fees, regime-aware leakage and look-ahead checks, untouched out-of-time/test-market datasets, negative-case/no-edge demonstration.
- Independent security review with controlled test sandbox, malicious source injection, code/dependency review, secrets review and signed artifact outputs.
- Applicable exchange market-data rights and India SEBI RA/IA/retail-algo/MTF legal review; company trading/advisory and investor-facing features require different licensing. Research-only product launch does not imply trading authorization.

**P1 product work:**
- Permissioned broker connection wizard verified end-to-end in at least one supported host; explicit notice that free Zerodha Kite MCP is distinct from paid Kite REST API and host MCP credentials do not automatically populate Fundtex CLI.
- Instrumented agent lifecycle in Claude/Codex/Gemini with actual true host name; opt-in viewer defaults OFF; logout/kill, rotation, accessibility and privacy reviewed.
- Independent source redundancy where legal: new `fundtex reconcile` compares two user-approved date-close histories with source SHA256, overlap, symmetric bps and mismatch ledger; four isolated tests passed. It cannot certify genuine vendor independence, calendar/corporate-action adjustments or data licences. Add comparable OHLCV, market holidays and issuer actions before release; never "scrape until accurate".
- Separate educational habit and trade-journal reflection module; no health or spiritual claims of guaranteed financial success.
- Gate performance against a real professional analyst workflow; don't claim Bloomberg parity based on a checklist of features.

## Compliance note (do not inherit old Fundtex claims)

Some early project files describe deliberately disguising simulation as real trades, a guarantee that the house always wins, 100x leverage as safe, or hiding planned crypto incentives from regulators. None is acceptable as a product or legal premise. India's **retail algorithmic trading** framework applies from **1 April 2026** under SEBI's 30 September 2025 implementation circular; exchange procedures and vendor empanelment also matter. MTF is a licensed broker/depository product subject to collateral and eligible securities rules, not a magic 100x options-loan facility. Confirm primary current rules with specialist counsel before launching funds, trading, advice, user-linked rewards or margin.

References: 
- https://github.com/monid-ai/monid
- https://github.com/cloudflare/security-audit-skill
- https://github.com/google-research/harness2
- https://www.sebi.gov.in/legal/circulars/sep-2025/extension-of-timeline-for-implementation-of-sebi-circular-dated-february-04-2025-on-safer-participation-of-retail-investors-in-algorithmic-trading-_96979.html
- https://www.nseindia.com/static/trade/platform-services-non-neat-decision-support-tools-algorithm-trading
- https://www.nseindia.com/static/trade/empanelled-algo-providers-exchange

**Release determination as of this audit: NOT YET APPROVED.** Keep `main` untouched until independent testing passes.