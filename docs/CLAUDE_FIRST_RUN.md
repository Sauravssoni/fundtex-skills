# Fundtex — Claude Code / Codex First-Run Acceptance Contract

**Terminal-enabled Claude Code or Codex only.** Ordinary Claude web chat cannot install local CLI software just because a prompt asks it to. If terminal tools are unavailable, explain the limitation and supply the exact command for a supported local environment. Never claim an install that did not run.

## When asked to install Fundtex

1. Check terminal permission, working directory, Python >=3.9 and whether the repository already exists. Do not clone over or overwrite existing files. Confirm origin is https://github.com/Sauravssoni/fundtex-skills and preserve uncommitted changes.
2. Read README.md, AGENTS.md, CLAUDE.md, install.sh, docs/FIRST_SESSION.md and docs/VALIDATION.md. Inspect install.sh before execution. No brokerage API keys or client portfolios required.
3. Run bash install.sh; check exit status; then run the full-path command below from the checked-out repository root:

       "$HOME/.local/bin/fundtex" doctor --repo-root "$PWD"

   All nine India skills should be present in each supported agent directory and the installed engine should match the checkout. If versions differ, do not overwrite without approval: use the repository's Python CLI temporarily.
4. Immediately demonstrate two working **fictional, clearly labelled** forensic reports (not price prediction or actual listed companies):

       python3 -m fundtex_india.cli diligence --inputs examples/india_company_diligence_SYNTHETIC.json --format markdown
       python3 -m fundtex_india.cli diligence --inputs examples/india_bank_diligence_SYNTHETIC.json --format markdown

   Identify useful real analyst checks: cash conversion, receivables, debt/EBITDA, lender GNPA/NNPA, credit cost and capital. No invented live quotes.
5. Run python3 -m unittest discover -s tests -p 'test_fundtex*.py' -v. Optionally run heavier million-path numerical and 60-regime stress after the first useful output or when the user requests it.
6. Present a concise verified status, a short example of the fictional analysis, three relevant first real-research questions using only actually accessible permitted context, and one next question: "Which company, sector or research task should we tackle first?" If history isn't available, say so and use useful defaults.

## On the first real Indian company request

Use the host's authorized web/source tools to locate and actually open current NSE/BSE issuer disclosures, investor relations financial results and material dated RBI/SEBI context. Verify ticker/ISIN, publication timestamp in IST, FY/Q quarter, group/standalone and INR crore/lakh units. Never claim that reading this skill already connected a paid or licensed market-data feed.

Give: executive research finding; dated evidence ledger; financial statement and cash conversion; actual disclosures; bull/bear/unknown; valuation and source assumptions; main invalidators; risks/catalysts; quantitative checks where authorized price history exists; missing and contradictory evidence; analyst review/abstention.

For deep work, use the optional bounded multi-agent council when supported and authorized; otherwise Source → Financials → Quant → Independent Skeptic sequentially. No uncontrolled delegation, secret or portfolio exfiltration, automated trades or unverified predictions.

## Fallbacks and first-run honesty

| Blocker | Workable response |
|---|---|
| No terminal or skill discovery | Explain Claude Code/Codex requirement and manual command; never claim installed |
| Installed engine stale | Use checked-out CLI until approval to replace installed snapshot |
| No fundtex on PATH | Invoke absolute $HOME/.local/bin/fundtex |
| No market data or Yahoo 429 | Use approved offline records or sourced research mode; never invent prices |
| No subagents / cost limit | Execute bounded expert roles sequentially |
| Confidential company/client data | Request firm approval or de-identified permitted inputs |
| No verified directional edge | Say ABSTAIN; describe what would falsify forecasts |
| Failed tests | Report exact failure and stop claiming production readiness |

First-run QA should verify: source origin, safe installer exit, skill paths, doctor healthy, two distinct fictional reports, tests, three real first-task suggestions, no unsupported price/alpha claims and no public private-plugin files.

No software can honestly promise superiority over Bloomberg or guaranteed profits without independently validated market data, analyst workflows and performance.
