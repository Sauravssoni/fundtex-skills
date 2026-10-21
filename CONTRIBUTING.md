# Contributing to Fundtex Financial Intelligence

We welcome reproducible research, India-specific equity/sector analytics, data-quality safeguards, accessibility and developer-experience improvements. The goal is **trustworthy analyst utility**, not the loudest prediction claim.

## Before proposing a change

1. Read AGENTS.md, CLAUDE.md, docs/SELF_EVOLUTION.md, docs/VALIDATION.md and the relevant SKILL.md.
2. Describe the analyst pain point, sources required, Indian-market specifics, expected behavior and likely failure mode. Give sources and as-of timestamps.
3. Open an issue or independent feature/research branch. Do not embed licensed/exchange data, private client documents, account secrets or proprietary plugin code in the public repository.
4. Add offline tests for happy-path, erroneous inputs, leaking future prices, missing source records, failure fallback and deterministic reproducibility.
5. Quantitative forecasting changes must include baseline Brier/log-loss/calibration, held-out benchmark comparisons, ablations, cost modelling and explicit negative results. Do not use hidden test periods for tuning.
6. Run: python3 -m unittest discover -s tests -p 'test_fundtex*.py' -v. Optional heavy gate: RUN_MILLION_TEST=1 python3 -m unittest -v tests.test_fundtex_million. For synthetic regime robustness: python3 -m fundtex_india.cli evaluate --scenarios 36 --sessions 540 --seed 42.
7. Submit a concise change summary, test results, source rights, impact on users and rollback plan. No automated merge or execution of live trades.

## Skills architecture

- fundtex-* SKILL.md files: India-first behavior, primary-source hierarchy, agent fallbacks and professional reporting.
- fundtex_india: dependency-light Python research CLI and simulations, source-quality markings.
- trader-* directories: retained Jake Schincariol original MIT-licensed US skills. Preserve copyright notices and attribute upstream before modifying.
- tests: offline deterministic contracts, synthetic input fixtures, error behavior.
- docs: provenance, empirical failure disclosures and professionally reviewed operating protocol.

## Pull request quality gates

Code readable; functions bounded; no fabricated facts; no unexpected network or private-data operations; exact sources and timestamps; failure paths tested; reported numeric evaluation reproducible; tests green; sensitive data absent; no unlicensed datasets, scraped closed APIs or claims of guaranteed returns.

Fundtex branding and the private ChatGPT plugin are separate. No plugin package, account-specific release manifest or private website code belongs here.
