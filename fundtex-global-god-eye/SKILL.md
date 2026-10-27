---
name: fundtex-global-god-eye
description: Link World Monitor world risk, country brief, macro, market, maritime chokepoints and news intelligence to India's actual issuer/exchange evidence without false geopolitical alpha.
---
# FundTex Global God Eye — Source-linked Macro/Geopolitical Context

FundTex's original macro-risk research layer. Upstream service: https://worldmonitor.app/mcp by koala73/worldmonitor (**AGPL-3.0**, source code NOT bundled). It supplies optional evidence only after its independent OAuth/account access and terms are satisfied. Official server supports `get_sources` discovery without user key; most data tools require subscription entitlement. Don't claim premium tools work until the actual host verifies permission.

**One-question onboarding:** If a user's host supports authorized remote MCP, guide consent to World Monitor once. Find tools by genuine registration and ask for the smallest needed scope. Otherwise cite dated independently accessible official sources or request an approved JSON snapshot. Never request API keys/tokens in chat. Don't use generic arbitrary HTTP fetch on user-private dashboards.

**Five analyst lenses:** (1) shocks and publication clock, (2) energy and shipping chokepoints for INR/imported inflation, (3) country risk and global rates, (4) sector/issuer exposure with documented contracts or filings, (5) contradiction tests. A Middle-East shipping disruption can motivate *research* into crude or transport risk; it is **not** evidence that NIFTY must decline tomorrow. Document source/observed/publication timestamps, stale caches, licensing, second-order transmission hypothesis and invalidators.

Where the host legitimately retrieved provider data, normalize a **small attributed event subset** using `fundtex fusion-desk --events /approved/source-events.json --symbol ...`; never automatically write raw full licensed feeds to public GitHub or export sensitive user data. Every report states which World Monitor tools actually ran, distinguishes its cached timestamps from real market timestamps and separates contextual correlations from causal claims.

Escalate to the existing `fundtex-god-eye` and `fundtex-analyst-council` skeptics for bull/bear/unknown hypotheses. Only authorized brokers provide verified exchange quotes. No write tools, no trade execution, no surveillance or speculative targeting.
## Optional direct CLI World Monitor bridge

On a user-authorized terminal with network access, `fundtex world-monitor --tool get_sources --out /approved/NEW-world-sources.json` retrieves the official **public** source directory with a SHA256 receipt, no key required. For actual user-entitled risk/news/market data, obtain user's permission and ensure `WORLD_MONITOR_API_KEY` was set privately in their local host (do not paste it in chat): `fundtex world-monitor --tool get_country_risk --inputs /approved/country-IN.json --out /approved/NEW-risk.json --approve-entitled`. A JSON argument file can contain `{"country_code":"IN"}`. The adapter validates tool and argument allowlists and does not expose account or order tools. Provider data-bearing calls may fail due to entitlement or quotas; don't improvise. Responses saved locally are **not cryptographically authenticated or authorized for redistribution**. ChatGPT web should use the host's OAuth plugin tools rather than request a plaintext key.

`fundtex fusion-desk` accepts a **reviewed, reduced, source-tagged JSON list of EVENTS**, not the entire World Monitor `get_sources` tool result. Agents must transform only actual dated events with licensing permissions; no source-only response should be misrepresented as a live event.
