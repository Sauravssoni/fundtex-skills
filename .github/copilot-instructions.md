# Fundtex Public Skills — Copilot agent instructions

For any natural-language Indian finance analyst request, follow docs/AGENT_NATIVE_V1.md and fundtex-auto-analyst/SKILL.md: run the single approved-source research workflow, inspect actually generated report files and broker freshness status, and cite original issuer filings for fundamentals. Do not send the user hunting for scripts or install dependencies silently. An official Kite/Dhan quote is a separately authenticated snapshot; unofficial public Yahoo daily prices are NOT exchange-certified live data. The default user experience is agent-native, not a dashboard.


Read AGENTS.md (canonical), docs/CLAUDE_FIRST_RUN.md (installation/first use), and docs/AGENT_PORTABILITY.md (agent-specific behavior). Preserve original MIT attribution; do not copy private ChatGPT plugin code or client records into this public repo.

When asked to install: verify actual terminal permission, inspect installer before running, validate doctor --repo-root and provide the two fictional fundamental company/bank demos. Suggest three appropriate research tasks; never pretend to read inaccessible chat history or confidential employer sources.

For Indian research prioritize real NSE/BSE issuer filings, RBI/SEBI publication times, forensic cash conversion, working capital, governance, bank/NBFC capital and asset-quality ratios and scenario-dependent valuation. Cite opened primary documents. No live exchange feed is bundled; no trading or verified alpha.

Use the offline Fundtex mission CLI to propose specialist tasks. Subagents may execute only if the user and host authorize them; otherwise perform Source, Financials, Quant and Skeptic passes sequentially. Before code changes, run tests, preserve failure disclosures and get approval for model promotion or live institutional integration.
