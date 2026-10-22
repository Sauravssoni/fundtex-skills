# FundTex Autonomous Agent Release Gate — 23 October 2026

## Product UX

One installed FundTex skill suite gives compatible terminal-enabled Claude Code, Codex, Gemini CLI and other capable coding hosts access to **21 India financial research skills + 11 legacy trader skills** and a pure Python finance research engine. The human asks a question in natural language. The AI should select the skill, inspect actual tool/entitlement access, compute accurately, verify output, and deliver a file/report without making the user run code.

**The skill cannot grant host terminal access, permanent agent identity, self-executing plugins, live broker credentials, a licensed NSE/BSE feed or guaranteed strategy alpha.** It is a local research assistant workflow, not a registered advisor or broker.

## What this branch fixes

- `bash install.sh` now packages `docs/`, `examples/`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` and README into `~/.local/share/fundtex-intelligence` alongside the Python engine, with no implicit overwrites.
- `--upgrade` is explicit and moves old reference copies into a backup folder.
- `fundtex doctor` checks actual source references, engine drift, launcher and all 21 installed India skills; exposes `autonomous_first_run_ready`.
- `fundtex-auto-analyst/SKILL.md` resolves absolute installed paths, defaults to permitted public history when broker is unconfigured, and uses authorized tools for historical returns, reports, strategies and skeptical committee review.
- `fundtex launchpad --out /approved/new/welcome.html --open` is a branded offline HTML welcome page with three example requests and official broker links. The user must explicitly request `--open` to launch browser. No JavaScript, local listener, dashboard prerequisite, broker login, personal data or API credentials are captured.
- Existing optional `activity-view` can display **real** lifecycle events only after the user opts in to host hooks. It must never invent agent activity.

## ChatGPT plugin separation

Authenticated private personal plugin **Fundtex Financial Intelligence** (ID `plugins_6ad87ebc3584819192317600d3635624`) was updated in place to **v0.6.0**, release `pluginrel_6ada72f77b5c8191ab35dd8c5446c220`. Verified from Plugin Creator: 17 skills, square SVG logo and composer icon, three default research prompts and an onboarding skill. Original plugin identity preserved. The private source mirror is `Sauravssoni/fundtex-website` branch `feature/fundtex-plugin-v06-autonomous-20261023`; **never publish that private package in this public repository**. Fundtex PayOS Developer is a separate merchant payments plugin, **not a duplicate**. No unrelated plugin was deleted.

The private ChatGPT research plugin **does not itself** execute local Python, install MCP hosts, authenticate a brokerage account, or expose private coding files. Those are permissions/capabilities of the connected host environment.

## Acceptance truth table

| Requirement | How verified | Scope |
| --- | --- | --- |
| Skills and references install | Isolated HOME clean install and upgrade test | Local Python test passed |
| Agent package version and skill count | Plugin Creator release metadata and file inventory | Release v0.6.0 with 17 skills verified |
| Logo and starter metadata | Source archive CRC, manifest paths; plugin service file inventory | Packaged, actual client UI render not verified |
| Optional browser welcome | User-approved `--open` smoke call and injection/no-overwrite tests | Browser open request succeeded |
| Broker quote and authorized live options chain | Not configured | **NOT VERIFIED** |
| Independent real-market option backtest | Entitled historical instrument chain missing | **NOT VERIFIED** |
| True lifecycle hooks | Test hook bridge and local viewer exist | Real all-host adapters still require opt-in verification |
| Truly institutional Bloomberg parity | No complete external benchmark or licensed data-feed evaluation | **NOT CLAIMED** |
| Investment/trading regulatory permissions | Primary current legal review needed | **NOT CLAIMED** |

### Core runbook for a test user

1. Clone **only** the public `fundtex-skills` repository and inspect `install.sh`. The advanced release is currently on `feature/fundtex-autonomous-release-20261023` (review branch, not public main).
2. Run `bash install.sh` in a safe authorized shell, optionally `bash install.sh --upgrade` only with explicit backup-first approval.
3. Restart the coding agent if required by its skill-discovery cache. Ask: *"Analyze INFY.NS, verify dated sources, chart prices, stress the bear case and prepare the analyst pack. Use public historical data if I have not connected my broker."*
4. Inspect the actual data/manifest/exports. Show a usable result and clear deficiencies; don't use fictional fallback data as though real.
5. If the user requests an optional welcome window, the agent may generate the new launchpad in an approved directory and open it with user approval.

Keep `main` untouched until source entitlement, CI and full artifact visual QA pass. This is a high-quality **research preview**, not a regulator-certified live trading platform.
