# Fundtex — First Session: Context-Aware Onboarding

An analyst should immediately receive useful research actions, not a generic promotional tutorial. The shell installer prints three safe starter questions; CLI onboarding offers deterministic recommendations from explicitly provided task context. An agent that installed Fundtex must *also* proactively suggest three research prompts after validating the installation.

## Recommended steps for Claude or Codex

1. Inspect README.md, AGENTS.md, install.sh, third-party licences and docs/VALIDATION.md; check if checkout and installed copies already exist. Inspect changes; never overwrite silently.
2. With user permission, run bash install.sh, confirm exit code and check via the full-path CLI. Run tests in a bounded time budget.
3. Immediately after the install, state exactly what is working, what is not (e.g. no verified live NSE feed), and suggest THREE first questions based on the present request and any *genuinely accessible, authorized* relevant history.
4. Use first-party filings and documented approved data for the task the analyst chooses. A skill does not grant access to the analyst's past chats, employer database or broker data.
5. If context is unavailable, ask "Which of your everyday research tasks takes the most time?" and still provide three defaults for equity, portfolio and market events.

## Agent-compatible commands

    bash install.sh
    $HOME/.local/bin/fundtex doctor --repo-root /path/to/the/cloned/fundtex-skills
    $HOME/.local/bin/fundtex onboard --context "Indian NBFC and banking earnings analysis"
    $HOME/.local/bin/fundtex council --mode DEEP --max-workers 5 --parallel
    $HOME/.local/bin/fundtex evaluate --scenarios 6 --sessions 400 --seed 42
    python3 -m unittest discover -s tests -p 'test_fundtex*.py' -v

## First prompts by analyst job

| Analyst | First question |
|---|---|
| Equity research | Build a source-linked bull/bear/unknown case for a company I specify; reconcile cash flows, auditor statements and valuation assumptions. |
| Banks / NBFC | Compare credit quality, GNPA/NNPA, NIM, capital and funding risks of two Indian lenders using dated primary filings. |
| Portfolio analyst | Stress test an authorized holdings CSV for sector concentration, risk contribution, correlation and cost sensitivity; disclose missing information. |
| Corporate events | Find and verify material NSE/BSE filings this week for a specified watchlist, citing filing release times and contradictory reports. |
| Quant | Evaluate a sourced historical price series, Brier score against simple probability baselines, interval calibration and actual backtest failures. |
| Macro | Trace fresh RBI rates, INR and commodity effects into relevant listed Indian sectors with a rival causal explanation. |
| Investment committee | Generate a two-page decision-support memo with verifiable evidence, financial risks, bull/bear triggers and reviewer sign-off questions. |

## Fallback contracts

| Blocker | Verified alternative |
|---|---|
| Skill discovery not supported by agent | Read SKILL.md manually and use Python CLI inside checked-out repo |
| fundtex executable not in PATH | Use quoted $HOME/.local/bin/fundtex or python3 -m fundtex_india.cli |
| Existing outdated installed engine | Analyze from fresh clone; seek approval before replacing installed copy |
| No network / exchange source inaccessible | Work from authorized local filings/CSV; mark external source verification pending |
| Yahoo feed HTTP 429 / price source unreliable | Stop; use a legally sourced exchange or broker export. Never invent a quote |
| No subagent feature | Sequential Source → Financials → Quant → Skeptic |
| Confidential client portfolio | Ask for de-identified or firm-approved data; don't upload automatically |
| No demonstrated predictive edge | ABSTAIN; identify what future observations would validate/falsify the hypothesis |
| Unsupported Python/runtime | Provide manual source-research checklist, never imply computations ran |

## Delivery quality

The first result must be concise and immediately actionable. Full studies provide as-of IST, audited evidence, forensic financial quality, major scenario assumptions, opponent thesis, meaningful quantified risk, confidence limitations and recommended human review. Never overstate predictions or transfer US tax/broker rules to India.
