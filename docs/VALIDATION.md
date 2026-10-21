# Fundtex Validation Ledger — 21 October 2026

Environment: MacBook Pro, macOS, Python 3.11, isolated QA clone. No broker credentials, production trading or private institutional portfolios accessed.

## Verified local engineering

- **64/64 local Python tests PASSED** including offline NSE UDiFF and historic Google Finance-style importers, source SHA-256 receipts, prequential probabilistic forecasts, no-future-price checks, financial analysis and GOD EYE walk-forward contracts.
- **1,000,000 seeded Gaussian scenario draws PASSED** in **3.17s** in the v0.8 64-test suite. This is CPU computation, not one million actual backtested trades.
- Final temporary-HOME installer verification copied **19 skills into 3 agent skill locations (57 copies)**, then safely skipped all 57 on a second run; the installed evaluation CLI succeeded without any writes into the user's actual home directory.
- Google News source discovery succeeded over HTTPS on one test. RSS headlines are unverified leads. Unofficial Yahoo prices returned HTTP 429 and are not reliable for production.
- Hosted GitHub Actions previously failed before running any steps; CI is not established as green.
- Four third-party historical Indian equity/index archives, ending 2021-01-25: original GOD EYE underperformed buy-and-hold in all four; prequential positive-day-frequency model failed superiority versus an expanding historical-frequency baseline in all four. The research confidence gate ABSTAINED on all four. See EMPIRICAL_RESEARCH.md.
- Exchange licensing, adjustments for dividends/splits, point-in-time universe, signal timing, legal suitability, delistings, slippage, liquidity and real client controls are NOT verified.

## Final v0.5 user experience and privacy verification

The installer was executed twice under a fresh disposable HOME. The first execution copied 19 unique skills into Claude, Codex and shared agent directories (57 copies), printed three immediately usable research prompts, and installed a CLI that passed the offline doctor, contextual onboarding and bounded 5-worker Council task planner checks. The second execution skipped all 57 existing skill files safely. The Council generates a plan rather than spawning workers; it does not read old chats, local private records or external accounts.

## Adversarial six-regime stress evaluation

A separate 2,000,000-path seeded Gaussian computational stress run also PASSED in 8.51 seconds on the test Mac (5-session hypothetical horizon); it is not two million real historical trades.

60 fully synthetic scenarios generated 32,400 price observations and 25,140 prequential forecasts. All 60 correctly withheld prediction approval under a strict baseline-superiority gate; mean Brier skill was -0.4345% versus the expanding-frequency baseline. See [full stress benchmark](STRESS_BENCHMARK.md). This is software robustness evaluation, **not market prediction accuracy**.

## Financial analyst diligence QA (v0.6)

The ninth India-specific skill, fundtex-india-diligence, is installed alongside the existing eight India skills. Together with the 11 attributed upstream skills, the v0.6 distribution has 20 SKILL.md folders. Fresh clean-install verification PASSED: 60 skill copies across Claude/Codex/shared agent locations, 60 non-destructive skips on reinstall, nine India skills detected in each agent directory, matching engine versions, and both fictional company and lender reports executed successfully.

Fundtex's separate offline company diligence tool successfully processed deliberately fictional Indian operating-company and banking examples. It reproduced revenue growth, cash conversion, negative FCF, net debt/EBITDA, high receivables review questions, and banking-specific GNPA/NNPA/credit cost/capital ratios. Unit tests reject nonfinite, boolean, unknown or unverified input status, and source links remain labelled not independently opened. This validates arithmetic/contract behavior only: no real issuer financial statement authentication or institutional sign-off has occurred. See COMPANY_DILIGENCE.md and CLAUDE_FIRST_RUN.md.

## v0.7 Portable Agent Mission Control (planning only)

Added GEMINI.md, Cursor .mdc rule, Copilot repository instructions and a dedicated Fundtex Analyst Council skill, plus deterministic Mission Control for explicit host capabilities, user permission, bounded specialist roles and fallback paths. Nine additional tests passed since v0.6: all 53 tests including million-draw numerical computation. These tests confirm deterministic plan construction and no raw task echo, not live agent-spawn execution. See AGENT_PORTABILITY.md and ANALYST_DELIVERY_CONTRACT.md.

## Final v0.7 cross-agent installer regression

The v0.7 full unit run passed **53/53 tests** including an isolated disposable-HOME install of **21 unique skills to three agent locations (63 installed files)**, a repeat that safely skipped **63 existing copies**, matching CLI version checks, all ten India-first skill files, a verified installed Mission Control command that returned a bounded sequential plan, and checks that no private plugin manifest exists in the public repository. This does not constitute a live full Claude/Codex/Gemini/Cursor session trial, subagent spawn or financial-data feed validation.

## v0.8 official source + benchmark verification

- 64/64 Python tests passed with the 1,000,000-draw synthetic numerical gate (3.17 sec on this Mac during first full suite).
- 23 public SKILL.md folders (12 India-first plus 11 attributed original), 69 skill copies across Claude/Codex/shared-agent directories and 69 safe skips on repeated install were exercised in temporary isolated HOME through the complete test suite.
- AMFI parser passed a smoke test using an **actually observed** official-site eight-column HDFC Corporate Bond Fund Direct Plan Growth NAV record dated 19 October 2026. Only parsing of that publicly displayed row was tested; neither a full current NAV batch nor data rights were independently approved.
- Official RBI and SEBI feed URLs were verified as publisher-supported; a live Mac-network request failed with URLError. The offline XML parser, bounded allowlist and fallback passed. No claim of a working live regulatory deployment.
- Synthetic human workflow benchmark inputs generate an explicit NOT_REVIEWED_DO_NOT_ADVERTISE flag. Actual sister/institution baseline measurements are not yet provided; no time-savings claims can be made.
- Optional MCP v2 sandbox and tool logic are unit-tested without SDK. The actual external MCP SDK, host handshake and external agent calls have NOT yet been end-to-end validated.
- New tests validate source schemas, poisoned XML rejection, HTTPS requirements, AMFI scheme freshness, NAV invalid numeric rejection, benchmark rejection criteria and no arbitrary MCP file access.

## Current predictive classification

**No demonstrated predictive alpha.** Near-80% historical coverage for an 80% return interval does not prove directional skill. Third-party archives are older than five years and have not been independently reconciled to official corporate actions; no claims about today's market follow.

The offline NSE UDiFF importer reads user-provided ZIPs and checks columns, equity series, duplicate dates and ISIN stability. It does not certify exchange authenticity, market data redistribution rights or corporate-action-adjusted returns.

## Institutional go/no-go gates

1. Obtain licensed/authorized NSE/BSE institution-grade prices, revisions, company actions and ISIN master.
2. Add independently verified primary financial disclosures and publication timestamps.
3. Conduct blind, time-causal, multi-asset walk-forward tests against credible baselines with Indian execution charges and impact.
4. Report prospective paper-trial calibration, costs, opportunity-matched benchmark and all failures.
5. Complete SEBI RA/IA, data-licensing and privacy/cybersecurity checks as applicable.
6. Separately verify live website route and hosted CI; a Git commit and a local build do not establish deployment.

**Verdict:** increasingly useful and testable research software, NOT an investment prediction product certified for institutional recommendations. A conservative ABSTAIN is preferable to an unsupported profit claim.

Eleven original US skills copyright Jake Schincariol, MIT. Fundtex India modules developed by Syntheon Technology.
