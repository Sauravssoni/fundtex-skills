# Fundtex Financial Intelligence — Agent Operating Contract

Company: Fundtex Financial Intelligence, an initiative within Syntheon Technology Private Limited.

This PUBLIC repo contains Claude/Codex-compatible SKILL.md files, source-attributed Python research code, test fixtures and documentation. Keep ALL ChatGPT plugin manifests, implementation, release archives and account information on the separate PRIVATE Sauravssoni/fundtex-website branch feature/private-fundtex-chatgpt-plugin. Do not copy private plugin assets into this repository.

## v1.0: one natural-language request, autonomous approved-source research

When a user asks to analyze an Indian company, do not direct them to scripts or a separate dashboard. Read docs/AGENT_NATIVE_V1.md plus fundtex-auto-analyst and fundtex-india-live-data SKILL.md. Verify the company ticker/ISIN, current authorized host shell, source rights and installed Fundtex version. Run fundtex research --symbol VERIFIED.NS --source public --quote auto --out /new/report (from the agent terminal) to fetch actual best-effort dated public historical prices, optional already-authorized Kite/Dhan LTP snapshot, source-labelled charts, evidence ledger and ZIP pack. If public fetch fails, fail clearly rather than substitute synthetic data; if broker not configured, label NO_CONFIGURED_BROKER. Optional XLSX/PDF/PNG renderers must be checked against actual files and manifest. A read-only broker snapshot is NOT WebSocket streaming, and a chart does not verify issuer earnings. Have an independent skeptic check every conclusion and open actual dated NSE/BSE/issuer filings with permitted tools before material fundamental claims. Never transmit secrets or private employer data without explicit authorization. Existing installer state may be stale; explicit bash install.sh --upgrade backs up before refresh and requires user approval. No standalone dashboard is part of this default.

## Handoff priority: show working financial research in the first session

**Read docs/CLAUDE_FIRST_RUN.md first.** This is a working acceptance contract for Claude Code/Codex with terminal access, not ordinary Claude web chat. If terminal unavailable, never pretend to install. After permission and safe install, use the doctor command against the fresh checkout, run the small fictional company and bank diligence demonstrations, and give the user a concise real result plus three tailored first tasks. This takes priority over optional million-path simulations, full adversarial regime sweeps or exploratory refactors. Run larger tests when time and resources permit. Test failures must be disclosed.

**Company financial diligence CLI:** python3 -m fundtex_india.cli diligence --inputs examples/india_company_diligence_SYNTHETIC.json --format markdown . Fictional demonstration figures are not real market data. For actual company research, open primary issuer/exchange filings and prepare an analyst-approved input first; don't fabricate filing extraction.

## v1.0: automatic agent-first research (no dashboard dependency)

User messages such as "Analyze Infosys with the newest Indian price data, source-check disclosures, draw charts and give an Excel/PDF/CSV pack" should invoke fundtex-auto-analyst and fundtex-india-live-data directly. Verify actual NSE/BSE symbol and source. The agent runs `fundtex research --symbol INFY.NS --source public --quote auto --out /new/approved-folder` for best-effort dated history, or --source fyers --quote fyers with an explicitly user-authorized and previously configured FYERS app for authenticated daily OHLCV and a separate quote snapshot. Do not ask the user to hunt scripts or open a custom dashboard. FYERS and Angel One advertise free permitted API access for eligible account holders, but Fundtex contains no entitlements or passwords; the user must connect on their own local machine. Require dated source ledger, price adjustments caveat, original filing review and human skeptic signoff. Data returned from Yahoo is not a licensed realtime NSE feed. Read docs/AGENT_NATIVE_V1.md. Never auto-trade.

## v0.9: analyst output is a first-class deliverable

Read docs/ANALYST_STUDIO_V09.md. For chart requests run fundtex chart, report requests fundtex analyst-pack, user-approved portfolios fundtex portfolio and visual; screenshot after rendering use fundtex chart-screenshot only if the approved browser dependency works. Generate chart HTML/SVG/CSV/Markdown even when XLSX/PDF/PNG options aren't installed; report omitted files explicitly from the pack manifest. Check actual produced artifacts and visible rendering before claiming success. Do NOT invent OHLC or claim that localhost CSV refresh is licensed live exchange streaming. Every manual level and SMA crossover is historical/descriptive. For a boss-grade analyst pack require original verified issuer evidence and clear risks/unknowns; code cannot silently access private work history. The public repo contains no private ChatGPT plugin manifest.

## v0.8: source-verified financial-data research, never bypass licensing

Read docs/INDIA_SOURCE_CONNECTORS.md and docs/ANALYST_PILOT_V2.md. Before advising an analyst, run fundtex sources to inspect permitted source coverage. With user-approved network access the official SEBI/RBI RSS collector discovers publication metadata; full regulatory claims must be validated against the actually opened original. The network may be blocked: use the documented saved-XML fallback or mark unavailable, never fake a headline. For AMFI NAV use only an authorized downloaded text file, verify daily scheme date/plan/option and label file origin unverified until checked. Commercial NSE/BSE feeds require legal rights and must not be reverse-engineered or scraped around restrictions.

To prove usefulness, ask the analyst for one repeated daily workflow, then use human-review criteria, approved public/firm documents and a baseline in fundtex pilot. No fictional time savings presented as customer results. The optional MCP v2 tool server requires a separately installed official SDK and explicitly approved sandbox; do not silently modify host MCP configs, leak files, or enable remote access. If the user wants more integrations, prioritize verified source rights and reproducible evaluation over quantity.

## Maximum capability, without inventing capabilities

Across Claude Code, Codex, Gemini CLI, Cursor, Copilot and other agents, read docs/AGENT_PORTABILITY.md and docs/ANALYST_DELIVERY_CONTRACT.md. Use GEMINI.md, CLAUDE.md, .github/copilot-instructions.md and .cursor/rules/fundtex-research.mdc where your host supports them; a text file cannot grant subagents, shell/network, paid financial feeds or cross-chat memory.

For a serious research mission, first inspect your REAL host capabilities and authorization. Then invoke fundtex mission --task 'brief non-sensitive finance task' --agent generic --mode DEEP --abilities terminal,python --max-workers 5 --format markdown. Add web and subagents to abilities and --approved only if the host actually supports them and the user already authorized the data scope and costs. The mission CLI is a deterministic OFFLINE PLAN, not agent execution. Use specialist roles in parallel only when actual host tools permit; otherwise use sequential passes including an independent skeptic.

For software improvements, follow docs/SELF_EVOLUTION.md and tests: branch, hypothesis, baselines, adversarial/fallback checks, review approval. First deliver a working source-verified financial outcome whenever possible rather than spending the initial session on simulations or marketing. Source authenticity, sector correctness, open counterarguments and clear handoff are mandatory.

## Post-install first response and optional subagents

After a verified installation, do NOT stop at Installed. Proactively propose three specific high-utility research prompts based on the current user's task and authorized context already accessible in the host; if none is available, use defaults from docs/FIRST_SESSION.md and ask which daily workflow takes longest. The CLI command fundtex onboard --context 'authorized brief' generates three suggestions without accessing chat history itself. Do not infer or search past conversation, local documents or employer systems without permitted access. Explain if historical conversation data is unavailable.

For complex research, offer a bounded Analyst Intelligence Council: Lead / Source Auditor / Financial Forensics / Macro / Quant / Skeptic, using parallel subagents ONLY if host support, user permissions, confidentiality and cost allow; otherwise work sequentially. See docs/MULTI_AGENT_DESK.md. The lead reconciles source/time/accounting disagreements and must independently validate assumptions and dissenting evidence. This is not an unlimited spawn instruction.

Run fundtex doctor and report healthy/unhealthy installation, no live quote/data licence guarantees, then offer the user a ready-to-run example.

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
