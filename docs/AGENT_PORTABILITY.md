# Fundtex agent compatibility and fallbacks

No single prompt can guarantee identical behavior across different coding agents. This repository provides portable SKILL.md instructions, scoped agent context and a dependency-free Python research CLI. Feature discovery, agent spawning, network access, token budgets and employer file permissions remain controlled by the host and user.

| Host | Project instruction | Skill/path support | Boundary |
|---|---|---|---|
| Claude Code | CLAUDE.md | ~/.claude/skills | Requires local tool access; restart/reload an open session if needed |
| OpenAI Codex | AGENTS.md | ~/.agents/skills and commonly ~/.codex/skills depending version | Actual host skill discovery needs testing |
| Gemini CLI | GEMINI.md | ~/.agents/skills aliases | Documented default; existing workspace settings and security controls take precedence |
| Cursor | AGENTS.md, .cursor/rules/fundtex-research.mdc | Manual skill read or client-supported SKILL.md | Repository rules supported; global discovery varies |
| GitHub Copilot | .github/copilot-instructions.md and recognized agent files | Workspace/host dependent | Tool execution, skill loading and agent delegation vary |
| OpenCode/other terminal agents | AGENTS.md, manually selected SKILL.md | Host dependent | Fallback to the cloned Python module and Markdown protocol |

Useful official references: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview , https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md , https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/using-agent-skills.md , https://docs.cursor.com/context/rules , https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions .

## First use

1. Ask only for actual needed permissions; distinguish Claude Code/Codex terminal from ordinary chats.
2. Inspect origin, license and install.sh; preserve existing user files.
3. Run bash install.sh, then the installed CLI doctor with --repo-root set to this checkout.
4. Generate both marked FICTIONAL manufacturer and bank/NBFC diligence examples and confirm accounting checks.
5. Proactively offer three relevant research tasks based on permitted current context. Never fabricate prior-history access.
6. For a real company, use actually opened NSE/BSE/issuer primary documents and official RBI/SEBI context. No built-in licensed live quote feed.
7. For a complex task, use the Mission Control CLI below to design worker boundaries.

## v1.0 Automatic Indian market research (prefer to plans alone)

Agent-native workflow is now docs/AGENT_NATIVE_V1.md and fundtex-auto-analyst/SKILL.md. The user describes the question in natural language; the coding agent verifies ticker, source rights and installed version, invokes fundtex research with best-effort real public historical data or approved CSV, optionally adds authenticated Kite/Dhan quote snapshots if already configured, and returns actual report links. No separate dashboard. Mission Control remains a planner and is NOT proof of true agent spawning or licensed exchange market data.

## Mission Control

Run:
python3 -m fundtex_india.cli mission --task "Indian NBFC peer financial review" --agent generic --mode DEEP --abilities terminal,python --format markdown

Flags: --agent generic|claude|codex|gemini|cursor|copilot|opencode; --mode FAST|DEEP|INSTITUTIONAL; --abilities terminal,python,web,subagents,filesystem; --max-workers 1..6; --approved only when applicable user consent is already granted; --format json|markdown.

These flags DECLARE abilities; they do not enable them. Without explicit approval, Mission Control will not recommend web data collection or parallel-agent execution. It never creates workers or evaluates an investment thesis itself.

Fallback table: no terminal → manual repository instructions; no Python → qualitative sourced memo; no web → approved local documents/CSV only; no subagents → independent sequential specialist passes; no verified source/price → NOT VERIFIED; no verified edge → ABSTAIN. Avoid huge simulations during the first-use demo.

Existing installed snapshot differs from checkout? Never overwrite it without approval; run the checked-out module until change is reviewed. Confidential client financials must not be exported to unapproved AI platforms.
