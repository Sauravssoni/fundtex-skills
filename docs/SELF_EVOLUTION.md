# Self-evolving Fundtex — Controlled Research Improvement

Self-evolving means continuous **hypothesis-generation and verification**, not self-authorized model rewrites or autonomous trades.

## Evidence-to-release loop

1. Observe: user analyst issues, broken sources, failed citations, forecast calibration degradation, cost assumptions and compliance changes.
2. Hypothesize: propose a measurable improvement, failure cases, source licensing and predicted change against baseline.
3. Isolate: make changes on research/ or feature/ branch, never main; keep training, validation and independently held-out samples separate. Avoid tuning on final holdout and then claiming it was untouched.
4. Evaluate: run full Python tests, 1,000,000-path numerical test, multi-regime synthetic stress evaluator, real-data point-in-time licensed experiments, sector/asset/regime holdouts, turnover costs, delistings, corporate actions and publication delays.
5. Falsify: compare with fixed 50/50 and expanding probability-prior Brier scores AND correctly matched passive buy-and-hold/sector baselines. Require uncertainty and ablation studies. Run multiple-comparison correction for model search.
6. Gate: no change is automatically promoted because a synthetic scenario wins; needs demonstrated improvement on untouched data, human review and legal/data/security checks.
7. Deploy: paper-first, explicit opt-in, rollback receipt, version hashes and signed performance ledger. Monitor regime degradation and ABSTAIN when predictive validity cannot be demonstrated.

## Primary reproducible commands

    python3 -m unittest discover -s tests -p 'test_fundtex*.py' -v
    RUN_MILLION_TEST=1 python3 -m unittest -v tests.test_fundtex_million
    python3 -m fundtex_india.cli evaluate --scenarios 36 --sessions 540 --seed 42

The synthetic evaluator spans random-walk, bull, bear, mean-reverting, clustered-volatility and crash-jump regimes. Its score is a **software robustness metric**, NEVER a real trading performance score. Don't optimize on fixed evaluation seeds as though they were an independent future test.

## Indian institutional readiness

Provenance from permitted NSE/BSE or broker data; clean ISIN master; adjustments for dividends, splits, bonuses and survivorship; timestamp-accurate issuer filings and SEBI/RBI events; realistic Indian fees/STT/impact; approved analyst and firm privacy/compliance checks.

## Change request format

Idea, Indian market value, source rights, dataset timestamp cutoff, benchmark and cost assumptions, expected failure, patch references, test matrix and results, unexplained regressions, reviewer approval, rollback plan. Keep rejected experiments recorded.

The public repo MUST NOT store the ChatGPT plugin release archive, private app configurations, client documents or secrets.
