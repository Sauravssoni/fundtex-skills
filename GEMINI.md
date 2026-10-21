# Gemini CLI — Fundtex

Read AGENTS.md for the canonical Fundtex research and coding contract, docs/CLAUDE_FIRST_RUN.md for the first-use acceptance procedure, and docs/AGENT_PORTABILITY.md for cross-agent fallbacks.

For installation: require an authorized terminal; inspect install.sh, check repository origin and existing files, install without overwriting, run doctor against checkout, and demonstrate explicitly fictional Indian company and bank diligence reports. Then offer three useful prompts adapted only to context actually available and permitted. Never claim to know inaccessible past chats.

For a real India-company request: open relevant dated primary NSE/BSE/issuer disclosures using approved tools; mark missing source data NOT VERIFIED, reconcile INR and reporting periods, and challenge the thesis. Forecast alpha has not been demonstrated. No broker trading.

Use Mission Control for bounded work planning:
python3 -m fundtex_india.cli mission --task "Indian bank earnings quality and peers" --agent gemini --mode DEEP --abilities terminal,python --format markdown

Declare web/subagents only when supported and approved; the planner never executes or spawns workers. The default fallback is sequential review. Run tests after changes; focus on a useful analyst result before expensive simulation.
