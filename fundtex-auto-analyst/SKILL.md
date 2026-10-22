---
name: fundtex-auto-analyst
description: Use when a user asks Claude, Codex, Gemini CLI or another agent to analyze an Indian company, stock, bank or sector and automatically produce charts, latest permitted market prices, technical ratios, research brief, professional Excel/PDF where available and downloadable ZIP. Orchestrate real sources and skeptical specialist agents without users hunting CLI commands.
---

# Fundtex Auto Analyst — Agent-Native First-Run Contract

**Users speak ordinary English. Do not ask them to find scripts.** When a user says "Analyze Infosys and prepare a full investment committee pack", identify the actual NSE/BSE symbol (verify on a real public issuer/exchange page, not from assumption). If one essential ticker is missing and cannot be safely established, ask ONE clarification. Do not silently choose a similarly named ticker.

## First step — inspect real capabilities

- Confirm this agent has an authorized terminal and a Fundtex checkout or installed CLI. Read AGENTS.md, docs/AGENT_NATIVE_V1.md, docs/ANALYST_STUDIO_V09.md and relevant fundtex skills.
- Run the version/doctor checks against the latest checkout. Existing installations are intentionally not overwritten; inspect and obtain approval before upgrading.
- If no authorized terminal: explain what environment is needed; never falsely claim command execution.
- Do not pretend to know private chats, client accounts or employer data not actually accessible and authorized.

## Single user request → automatic analyst output

For current India historical evidence, prefer authenticated **FYERS** daily OHLCV where the user already has a permitted FYERS developer app; otherwise use the **best-effort public historical feed** when rights permit. FYERS documents free quotes, historical data and WebSocket access for eligible FYERS clients (authentication and account needed). See docs/AGENT_NATIVE_V1.md. One agent-side command (never ask user to memorize it):

    fundtex research --symbol INFY.NS --source public --quote auto --out /approved/new/fundtex-INFYN-20261021

This creates a new folder and ZIP with interactive SVG/HTML chart, historical close series, RSI/SMA, source-hashed CSVs, evidence/limitations, independent skeptic mission, Markdown memo and optional Excel/PDF/PNG. The output receipt states every omitted optional file. **Opening the generated files and checking accuracy is the agent's job**, not the user's.

For a permitted customer CSV use --source csv --csv /approved/input.csv. An actual source marked SYNTHETIC_FIXTURE MUST remain fictional, even if named a famous ticker. Never fall back to synthetic prices when the network is unavailable.

## Real-time prices require a real provider

- If authorized FYERS, Kite Connect or DhanHQ credentials are configured, --quote auto retrieves a read-only LTP snapshot without exposing credentials. Market streaming is NOT implemented by this skill or CLI.
- If no broker connected, explicitly label quote status NO_CONFIGURED_BROKER and keep the public historical chart separate.
- If the user explicitly requests a broker and it fails, fail closed. Do not silently return a public quote and claim it is authenticated.
- Distinguish observation date, retrieval UTC, authenticated quote timestamp if published, potential delay and any exchange market-data rights.
- A best-effort public Yahoo Finance chart request can return current-day historical closes but is NOT official or guaranteed real-time.



## First-run broker connection — must be conversational

Before asking a new analyst to supply an API token or run a script, call `fundtex connect` for the safe provider-choice catalog. Ask only: "Do you use Zerodha, FYERS, Dhan, or would you prefer public historical data for now?" Explain whether the selected data route is free, subscription-gated or account-specific.

- **Zerodha users in Claude:** Prefer Zerodha's official Kite MCP at https://zerodha.com/products/mcp/ for broker-hosted sign-in and read-only market information when available in that Claude client. Lead them through the official MCP install/authorize UI. Never request passwords or tokens. The Fundtex CLI cannot automatically consume a foreign MCP session; use verified MCP results in the host analyst workflow and keep data source attribution.
- **FYERS users:** Guide them to the official individual-app authentication process (https://fyers.in/api-docs/v3/getting-started/authentication/). Browser approval and secure local token setup are required; never solicit codes/secrets in chat. Then run `fundtex connect --provider fyers --verify INFY.NS` to verify a read-only quote after the user has configured it, and use authorized FYERS OHLCV history.
- **Dhan users:** Guide official Dhan Web Profile → DhanHQ Trading/Data APIs. Explain that market-data entitlement can require a paid subscription and a verified security ID mapping. Never subscribe, charge, or place trades for them.
- **Kite Connect developers:** Direct the user to the official Kite Connect auth documentation and explain the difference from broker-hosted Kite MCP; verify eligible market-data API entitlement.
- **No broker:** Continue with clearly labelled best-effort public dated history, and tell the user what cannot be claimed as live.

Agent must show only ONE next action at a time when guiding authorization, verify a real tool/quote response after consent, and only then say connected. Never claim `broker-status` proves authentication: it checks local configuration presence only.

## Professional review

Use any permitted exchange/issuer/RBI/SEBI official tools to open actual dated source documents, reconcile original filings, assess financial quality and company-specific risks. The CLI pack cannot extract or verify company financial statements automatically. Independent skeptic pass must challenge data timing, assumptions and meaningful contrary evidence before claiming any thesis. Specialized subagents are optional and require real host support; sequential reviewer passes are the default.

Return the report ZIP and concise decision-first summary with source ages, missing evidence and exact output links. Do not claim Bloomberg feature parity, autonomous trading or proven alpha.
