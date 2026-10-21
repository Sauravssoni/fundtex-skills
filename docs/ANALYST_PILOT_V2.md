# Independent Analyst Adoption Pilot — speed without hallucinations

Goal: measurable saving on the analyst's REAL everyday work without reducing correctness or confidentiality. Do not assert gains before human review.

1. Choose 3-5 comparable jobs: issuer earnings readout, bank/NBFC asset-quality comparison, new RBI/SEBI rule impact, valuation input audit, and portfolio-risk check.
2. Use the same dated original public/firm-approved documents, same source cutoff, reviewer and task scope for normal workflow and Fundtex.
3. Measure elapsed minutes, count expected facts from reference filings, correctly verified facts, unsupported claims, critical errors and primary originals actually opened. Reviewer checks each result independently.
4. Write only deidentified count metrics into an approved JSON file; keep employer/client material and raw transcripts PRIVATE and out of GitHub.
5. Run fundtex pilot --inputs /approved/analyst_pilot.json. Review computed time differences, factual recall, supported-claim precision, source usage and disqualifying errors.
6. Grade acceptance only if no critical errors, no drop in verified-fact coverage, unsupported claims no worse than baseline, and a real human reviewer approved the run.
7. If anything fails: document exact missing source or quality issue, fix on a reviewed research branch and repeat blind trial.

Example: examples/analyst_pilot_SYNTHETIC.json is FICTIONAL, not user-measured. Its claimed task timings are not evidence and it is marked NOT_REVIEWED_DO_NOT_ADVERTISE. The tool never independently validates the reviewer-provided numbers. Reviewer-approved scores remain reported rather than externally audited.

One question to the analyst: "Which one everyday finance research task takes you the longest? Let's measure time and accuracy against your current method on approved public/firm-permitted documents."

Actual issuer sources and market data remain subject to provider license terms. Speed improvements do not imply Bloomberg-equivalent coverage, legal permission to provide investment advice or validated predictive alpha.
