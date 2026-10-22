# Fundtex Validation Ledger — 22 October 2026

Environment: MacBook Pro, macOS, Python 3.11, isolated QA clone. No broker credentials, production trading or private institutional portfolios accessed.

## v1.0.1 broker onboarding verification — 22 October 2026

The broker connection experience is a conversational **guide**, not an OAuth app or a magical session bridge. It returns approved Zerodha Kite MCP, FYERS, Kite Connect and DhanHQ connection options with official URLs, access/fee caveats and clear privacy prompts; user consent and actual broker login remain required. `fundtex connect --provider FYERS|kite|dhan --verify INFY.NS` attempts a read-only quote only when local approved credentials exist; a mere env-variable presence is never displayed as authenticated. Zerodha Kite MCP is verified in the host Claude/MCP client, not the Fundtex CLI. Contract tests cover no-secret output, provider selection, no auto-open, unconfigured, quote successful, quote failed and third-party MCP detection. The final release suite on the authorized Mac PASSED **92/92 Python tests**, including the million seeded numerical draws (3.92 seconds for the draw portion) and agent-skill installation/backup contracts. User-credentialed broker login and true real-time WebSocket ingestion remain unverified and not claimed.

## v1.0 final free-data adapter and agent-native release gate — 22 October 2026

**84/84 full Python regression tests passed**, including the million-seeded-Gaussian-draw numerical suite (3.98 s for the draw itself) and 29-skill isolated agent installer/upgrade contracts. Additional FYERS official v3 REST API schema tests cover current LTP quote, dated OHLCV candle parsing, fail-closed missing authentication, wrong instrument, invalid candle bounds and no unsafe endpoint redirects. All FYERS tests used MOCK DATA and NO real client token; the provider connector is ready for a user-authorized free-tier account but a real FYERS quote was not claimed.

The **actual live-network one-shot CLI** `fundtex research --symbol INFY.NS --source public --quote off --out NEW_FOLDER` successfully generated a 12-file ZIP (**65,744 bytes**) with genuine best-effort Yahoo historical observations, a dated historical chart, source-hashed CSVs, source evidence ledger, PNG chart, research memo and agent mission. The latest observation returned in THIS final test was **19 October 2026** (2 calendar days old at retrieval), so the script **accurately reported its age and UNOFFICIAL_BEST_EFFORT_DELAYED status**, not a current real-time exchange tick. The 20 October NSE equities holiday is independently listed on the official NSE calendar; 21 October was a trading day, therefore data freshness must be checked rather than assumed. Browser screenshot, XLSX and PDF were unconfigured on the test Mac and **correctly listed as omitted**; previous separate portable v0.9 QA demonstrated those outputs with optional renderers installed. No user brokerage accounts or secrets were accessed. Re-testing at other times can return different latest as-of dates.

Publisher guidance: FYERS support says its APIs, including market data and historical, are no-extra-fee for eligible FYERS clients; its individual app access token is short-lived and the official API supports OHLC/quotes. Angel One SmartAPI also advertises a free data option; it is researched but NOT implemented in this release. Zerodha Personal API does NOT grant market data without its paid Connect subscription. DhanHQ data subscriptions are paid. Official NSE redistribution rights are NOT bypassed by free wrapper libraries. See docs/AGENT_NATIVE_V1.md and licensing links therein. Authenticated market-data snapshots are not continuously streamed.

## v1.0 — earlier verified engineering and real public market-data acceptance

**79/79 local Python regression checks passed** on 21 October 2026 after removing the obsolete dashboard-only prototype/test. The suite included a million seeded Gaussian draws in **5.07 seconds**. These are numerical tests, not trading returns or externally validated prediction performance.

The installer completed a **29-skill, three-agent-location** isolated HOME trial: **87 first installs, 87 non-destructive repeat skips, and an explicitly approved 87-skill backup-first upgrade**. The previous customized test skill marker survived in a retained backup. The installed engine version matched the fresh checkout. The user's actual HOME was not modified during QA.

A real best-effort Yahoo historical chart request succeeded for **INFY.NS** and reported the latest observation as **21 October 2026**. A three-month public-data end-to-end report generated **12 artifacts and a ZIP**, a dated source evidence record and a source quality of UNOFFICIAL_BEST_EFFORT_DELAYED with zero observed age at the test. The test expressly set quote_provider=off; it did not access or verify any user's private broker account. This is current historical market data, NOT a licensed realtime NSE stream.

Zerodha Kite Connect and DhanHQ v2 LTP REST snapshot adapters have unit tests for valid/missing quote responses, invalid instrument IDs, unauthorized endpoint rejection, and preventing credential material from appearing in outputs. **Actual authenticated provider calls have not been tested**, because no user-authorized credentials were supplied. Official broker quote documentation and data-usage rights must govern production use.

The one-shot CLI writes source-hashed HTML/SVG charts, historical CSV, descriptive technical observations, a skeptical research task plan, Markdown memo and a ZIP. An additional Pillow chart PNG is generated where the renderer is present. A true browser screenshot, styled XLSX and PDF use optional approved dependencies and are recorded as omissions when missing; no artifact is falsely claimed. Full automatic issuer-filing analysis still requires an authorized coding agent to open and verify actual original disclosures.

No new live tick-streaming feed, licensed market-data redistribution agreement, verified positive predictive alpha or autonomous trade execution was established. The product remains a research preview; it is not Bloomberg Terminal equivalence.

## Historical v0.8 local engineering

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

## v0.9 Analyst Studio source and artifact verification

- New component-level tests cover close-only charts that never fabricate OHLC, deterministic indicator calculations, labelled fictional source inputs, HTML/SVG rendering, source hashes, valid/invalid annotations, sector/matrix/waterfall/histogram SVG output, CLI-pack file existence, no-overwrite and malformed future/price data failures.
- 27 SKILL.md directories (16 India-first and 11 attributed original) are counted by the installer and the isolated skill-discovery test. Three supported agent directories imply 81 first installs and 81 safe skips; verified by rerunning the portability gate.
- On a separate isolated ChatGPT execution environment, the portable Fundtex Studio v0.9 source package produced a five-sheet XLSX, rendered PDF memo, screenshot PNG, browser-drawn level, SVG visuals, CSVs and source manifest using approved optional engines; 11/11 standalone tests passed, 240 seeded numerical price regimes checked, and 1,000,000 synthetic Gaussian draws completed. All demo figures are FICTIONAL and are not market performance.
- Mac CLI release dependencies reportlab/artifact_tool may be absent; optional deliverables are recorded as unavailable, never silently fabricated or auto-installed. Live NSE/BSE data and independent prediction validation remain unavailable.

## v0.9 final local release gate (21 October 2026)

**70/70 local Python checks passed** on the authorized Mac, including the million-seeded-draw numerical gate (4.83 s in that run) and disposable-HOME installation of all **27 skills** into three agent directories (81 copies) followed by 81 no-overwrite skips. A separately invoked end-to-end CLI test generated the synthetic close-only interactive HTML chart, core pack (SVG, HTML, memo, CSV, source receipt) and a sector pie SVG. The package correctly disclosed missing optional Mac screenshot/XLSX/PDF dependencies; no unverified image or workbook was invented.

The standalone portable v0.9 demonstration in a separate sandbox successfully generated XLSX, PDF, PNG and additional infographic SVGs with installed isolated tools, passed 11/11 studio tests, 240 seed-controlled data regimes and a million mathematical Gaussian draws. The interactive chart's manual level/clear controls were exercised in headless Chromium with no script errors. The demonstration is **FICTIONAL** and cannot establish real financial or forecasting performance.

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
