# Release history — Fundtex Financial Intelligence

## v1.0.1 — 22 October 2026
- Added agent-guided brokerage connection discovery for official Zerodha Kite MCP, FYERS, Kite Connect and DhanHQ, including broker-owned authentication steps, fee/entitlement boundaries and no token collection in chat.
- Added `fundtex connect` with optional user-approved official site opening and real read-only quote verification (when direct credentials are already user-configured). Configuration alone never proves an authenticated account. Zerodha MCP remains hosted in an authorized Claude/MCP client rather than magically bridged into the Fundtex Python process.
- Added eight contract tests covering provider choice, secret protection, connection failure, successful verified mocked read-only quote, and consent-before-opening. Final merged release suite **96/96 passed**, including the million-draw computational test and the new official Kite MCP agent-discovery contracts. Real client broker authorization and WebSocket tick streaming remain untested.

## v1.0 — 21 October 2026
- Reprioritized user experience as natural-language agent-native financial research; removed the unfinished dashboard from release rather than forcing a second interface.
- Added fundtex research automatic source-aware daily-price fetching, evidence ledger, historical chart, indicators, separate optional authenticated Kite/Dhan last-price snapshots, report folder and ZIP.
- Added source access, staleness rejection, synthetic-label retention and no-fallback-on-network-failure guards. Unofficial Yahoo public history stays classified UNOFFICIAL_BEST_EFFORT_DELAYED; neither source type constitutes licensed exchange real-time streaming.
- Added two discoverable skills for automatic analyst research and licensed-provider integration; 29 total skill folders, 18 India-first and 11 attributed upstream. Added concise universal one-prompt workflow documentation.
- Added explicit install.sh --upgrade with backup-first update of previous installed skills and engine; default repeated install remains no-overwrite.
- Added direct PNG historical chart rendering through Pillow if Chromium screenshot isn't available (not represented as a browser screenshot). Optional institutional XLSX/PDF packages still require approved installation.
- Full v1.0 suite: 79/79 local tests passed with million-draw numerical gate; isolated 87-skill installation, safe skips and backup-first upgrades passed. A real INFY.NS public Yahoo three-month historical request produced a 12-file research pack plus ZIP, dated 21 October 2026. Broker authenticated access remains unverified without user credentials.

## v1.0 — 22 October 2026
- Switched primary UX to natural-language agent orchestration. New one-shot `fundtex research` command generates source-ledgered dated Indian market chart, CSV, HTML, memo and ZIP, with separate optional credential-authorized broker LTP snapshot.
- Verified actual public Yahoo historical INFY.NS response (64 dated observations as-of 21 October 2026), labelled UNOFFICIAL_BEST_EFFORT_DELAYED. A live broker quote needs user credentials; no exchange license embedded.
- Added official FYERS v3 REST read-only quote and historical OHLCV adapters. FYERS advertises free API data access to eligible clients; individual login is required and tokens expire daily. Fully mocked protocol tests reject malformed OHLCV, invalid symbols and unsafe endpoints; real FYERS account integration remains untested until authorized.
- Added two agent-native skills, docs, backup-first explicit installer `--upgrade`, structured source evidence, automatic research-pack receipt and financial-data safeguards. No dashboard dependency.
- Additional full-suite test evidence in docs/VALIDATION.md. Private plugin remains isolated.

## v0.9 — 21 October 2026
- Delivered interactive self-contained research chart HTML/SVG; honest close-only line versus validated OHLC candlestick distinction; date/price validation, SMA20/50, EMA12/26, RSI14 and retrospective cross annotations.
- Added browser-side drawn levels and SVG/PNG/downloadable-notes export, optional Playwright screenshot and loopback-only local CSV refresh viewer (not a licensed real-time exchange feed).
- Added SVG graphics for sector pie, comparative bars, correlation heatmaps, historical return histograms and valuation waterfall from explicit user inputs.
- Added one-command analyst-pack with source receipt, price and historical crossover CSV, visual pack, Markdown memo and manifest. Optional vetted artifact_tool XLSX and ReportLab PDF; no silent dependency installation or unreported omissions.
- Added four agent skills and specialist operating contracts; public repo now 27 skills (16 India-first + 11 attributed MIT upstream), private ChatGPT plugin remains isolated.
- Added six studio-specific regression checks covering data integrity, XSS/annotations, graphics and end-to-end pack fallback. The full 70/70 local suite passed with a million-path numerical gate and clean 81-skill install/reinstall. End-to-end CLI chart, report pack and SVG pie generation passed; unavailable PDF/XLSX/browser extras were honestly disclosed on the Mac.

## v0.8 — 21 October 2026
- Added official read-only RBI/SEBI RSS event discovery with allowlisted HTTPS sources, timestamped metadata, input hashes, secure XML parsing, size/timeout limits and saved-feed fallback. Actual Mac live fetch returned a network error; live feed access remains unverified there.
- Added AMFI NAV snapshot parser supporting 2026 eight-column scheme, plan and option format and legacy six-column format. Validated a real observed public HDFC Corporate Bond Fund snapshot row (19 Oct 2026) as a parsing smoke test, without bundling publisher data.
- Added a de-identified analyst pilot scoring tool for baseline versus Fundtex research minutes, verified facts, unsupported claims and critical errors. Fictional metrics cannot be promoted as reviewed customer outcomes.
- Added optional MCP Python SDK v2 connector with explicit approved-directory sandbox, six read-only tools, no silent installation or arbitrary filesystem/network access; real MCP client handshake remains unverified.
- Added two specialized skills: fundtex-india-regulatory and fundtex-analyst-pilot (23 public SKILL.md total, 12 India-first).
- Expanded local regression to 64/64 tests including clean skill install/fallback, plus repeated numerical stress. No independently proven forecast edge or Bloomberg feed parity.

## v0.7 — 21 October 2026
- Added portable instructions for Gemini CLI, Cursor and GitHub Copilot in addition to Claude Code and Codex.
- Added Fundtex Analyst Council SKILL.md for discoverable role-based India research, plus mission CLI with tool/permission declarations, skeptical mandatory reviewer, output contract and sequential fallback.
- Added AGENT_PORTABILITY.md and ANALYST_DELIVERY_CONTRACT.md to make first-session and professional research quality expectations explicit, without claiming that instructions can grant host tools.
- 53/53 offline automated tests including million-draw computation; fresh temporary HOME installer passed for 21 skills in three destinations (63 installs), second run safely skipped all 63, and installed Mission Control executed. Live individual agent-client behavior remains untested.
- These capabilities produce plans and reliable calculations, not live exchange access, autonomous subagents, independent investment forecasts or proof of Bloomberg superiority.

## v0.6 — 21 October 2026
- Published the dedicated fundtex-india-diligence SKILL.md so Claude/Codex can discover and invoke the company-analysis workflow naturally.
- Added an actual India company diligence CLI producing Markdown/JSON analyst review packets from approved reported figures; includes distinct operating-company and bank/NBFC methods.
- Added intentionally fictional India company/lender examples to exercise cash conversion, receivables, leverage and asset-quality checks without manufacturing market data.
- Introduced a **Claude Code first-run acceptance contract**: validate terminal capability, safe install and version, immediately demonstrate the company/lender reports, then suggest three context-aware first research prompts before optional heavy simulations.
- Removed an unlaunched website route from public source references rather than exposing a broken link.
- Expanded local tests to **44/44 PASS**, and added fresh-checkout engine version comparison. Fresh v0.6 installer verification confirmed 60 skills installed and 60 safe skips, nine India skill files for every agent path, version match and two distinct financial diligence reports.
- This improves research usability and reproducibility, but does not certify Bloomberg-scale data access or predictive alpha.

## v0.5 — 21 October 2026
- Polished the public skills README for analyst-first installation, primary-source research and falsifiable quantitative evaluation.
- Introduced a contextual first-session onboarding program with three relevant starter prompts from **explicitly available/authorized** task context. It never searches a user's old chats or local files by itself.
- Introduced an offline doctor report for installed India skills, Python compatibility and CLI availability.
- Added bounded optional multi-agent Analyst Intelligence Council: primary filings, fundamental forensics, macro/sector, quant and skeptic; sequential fallback where unsupported.
- Added FIRST_SESSION, MULTI_AGENT_DESK, CONTRIBUTING, SECURITY and improved agent operating contracts.
- Expanded automated tests to **39 passing contracts** and verified 57 first-time skill installations, 57 safe no-overwrite skips, three starter prompts, doctor and bounded Council command in an isolated temporary HOME.
- Remains research-only. Predictive alpha and licensed exchange feed access NOT established.

## v0.4 — 21 October 2026
- Released 19 skills (8 India-first plus 11 preserved and attributed US trader skills), NSE-U​DiFF user-supplied ZIP and archived CSV source import, GOD EYE chronological policy lab, Forecast Lab probability calibration and scenario stress tester.
- Measured 30/30 regression contracts, 60 synthetic regimes, 25,140 chronological synthetic forecast scores and 2,000,000 additional mathematical scenario draws.
- Recorded failures of the simple directional model to outperform historical-frequency baselines in four archived third-party India samples ending in 2021; correct output is ABSTAIN.
- Separated private ChatGPT plugin from public skills.

## v0.1–v0.3 — October 2026
- Imported original 11 MIT-licensed trader skills, adding India source-quality validations, portfolio risk, DCF, historical VaR/ES, simulated distributions, news discovery, local installer and basic Claude/Codex skill pathways.

Note: historical test data and hypothetical market scenarios are NOT current market prices, independent prediction verification, personalized suitability advice or an investable performance record.
