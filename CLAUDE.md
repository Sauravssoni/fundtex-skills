# Fundtex Claude Code

Read AGENTS.md (canonical contract) and README.md before acting. This PUBLIC repository contains skills and a local read-only Python analytical engine. Private ChatGPT plugin source lives only on the PRIVATE fundtex-website feature/private-fundtex-chatgpt-plugin branch.

For installation, inspect bash install.sh, verify Python 3.9+, then run it with the user's permission and confirm skill paths and local CLI. Immediately thereafter, tell the user three genuinely relevant first research prompts from accessible authorized context and explain the source/fallback limits (docs/FIRST_SESSION.md). If host supports parallel subagents and the user permits it, use the bounded council in docs/MULTI_AGENT_DESK.md, or run its roles sequentially. Run the test suite and synthetic adverse-regime evaluator. Report what was actually run, its provenance, what failed, and next steps.

For improvements: open a proposed research/ branch, keep baseline and blind holdouts fixed, add reproducible tests, measure calibrated Brier/coverage AND passive-profit-risk comparisons, document negative results, and request approval before merge or updates to installed skills. Never auto-trade, manufacture current NSE prices or claim guaranteed alpha.
