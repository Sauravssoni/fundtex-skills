# Fundtex v0.4 — Reproducible Adversarial Scenario Benchmark

Evaluation date: 21 October 2026. Local Python evaluation. **All input paths are synthetic**, not NSE/BSE observations, and their timing includes synthetic calendar days.

## Recorded execution

    python3 -m fundtex_india.cli evaluate --scenarios 60 --sessions 540 --seed 20261021

| Verified measure | Result |
|---|---:|
| Synthetic regimes | 6 |
| Scenarios per regime | 10 |
| Total generated price observations | 32,400 |
| Chronological one-session forecasts scored | 25,140 |
| Mean Brier skill versus expanding-frequency historical prior | -0.4345% |
| Median Brier skill versus expanding-frequency historical prior | -0.5120% |
| Candidate model gates passed | 0 |
| Conservative model gates withheld | 60 |
| Execution time on local test Mac | 19.23 seconds |
| SHA-256 configuration | 50c5e4355841e87b440311e71bb7778ee7d12fab2dc541aca901cef8091efb60 |

Regimes: random walk, bull drift, bear drift, stationary mean-reverting latent price, volatility clusters and discontinuous downside jump shocks. Simulated models were not tuned after viewing these results.

## Findings

The empirical rolling direction model did not consistently beat the expanding-frequency prior under these scenarios. That is a **negative predictive result**, not a QA failure. All 60 output gates declined to certify an edge, which is the correct fail-closed behavior when the numerical evidence is weak.

The separate seed-fixed Gaussian path simulator was executed at one million paths as part of the **30/30 passing Python regression tests**. Those are mathematical draws, not historical trades or observed price forecasts.

## What this verifies

Correct deterministic output, documented failure/abstention, multiple synthetic regime handling, bounded CLI inputs, correlation to historical-prior baselines and reproducibility of adverse simulation outputs.

## What it does not verify

Live market direction, real source adjustment, cash/derivative trading profitability, NSE/BSE price accuracy, exposure capacity, fee completeness, calibrated security-specific probabilities, model robustness on future independent datasets or institutional suitability. Benchmarks measured on generated paths must never be represented as real-market returns.

See docs/EMPIRICAL_RESEARCH.md for a separate four-instrument historical data smoke test (all series end 2021 and source/adjustment integrity remains unverified). See docs/SELF_EVOLUTION.md for the controlled agent-driven research advancement protocol.
