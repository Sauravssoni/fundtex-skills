# FUNDTEX — Analyst Intelligence Council

**Optional multi-agent workflow, not a claim that every Claude/Codex host supports subagents.** Use parallel agents only when host capabilities and the user authorize them; otherwise execute the same steps sequentially. Never expose private investment records to extra workers without authorization.

## Modes

| Mode | When | Execution |
|---|---|---|
| QUICK | One company event or urgent question | One analyst, verify key primary sources |
| DEEP | Investment committee / complete diligence | Up to six independently scoped roles |
| QUANT | Historical series / portfolio audit | Numerical analyst + independent skeptic |
| COMPARE | 2–5 Indian companies | Parallel company analysts + cross-company reconciler |
| WATCHLIST | Filings, catalysts and risk monitor | Source-led watchlist, no scheduling without permission |

## CLI task-plan generation

Run the following from an authorized local checkout; it emits JSON for an agent to follow and does not execute any worker:

    python3 -m fundtex_india.cli council --mode DEEP --max-workers 5 --parallel

If subagents are unavailable or expensive, omit the parallel flag; the same workers can run sequentially. The task scope supplied to the CLI is deliberately not repeated in output to avoid leaking sensitive descriptions into logs. The host agent still needs user consent to access past messages or connected work files.

## Bounded specialized roles

1. **Lead/Editor** scopes question, permitted data, as-of IST, available context, research objective and deadline. Delegates only when useful.
2. **Primary-Source Auditor** examines actually opened NSE/BSE releases, issuer quarterly/annual disclosures, ISIN/corporate-action timelines, published date and source reliability. Aggregator headlines are leads, never a verified filing.
3. **Forensic Financial Analyst** compares operating cash flow to profits, working capital, receivables, related parties, debt/refinancing, auditors, governance, pledges and industry-specific metrics; no unproved fraud accusations.
4. **Macro/Industry Specialist** examines dated RBI/SEBI, FX/INR, oil/commodity, government policy, sector demand and supply, including alternative causal explanations.
5. **Quant/Risk Auditor** uses Fundtex read-only engine on approved CSVs, checks sampling, adjusted close, data hash, historical VaR, portfolio exposure, forecast Brier/calibration versus baselines, backtest costs and leakage.
6. **Skeptic/Red-Team Analyst** challenges the main thesis, identifies contradictory documents, overstated model significance, omitted risk and reasons to abstain.

The Lead may be the final Editor/Synthesizer. Four workers often suffice (sources, financials, quant, skeptic). Never recursively spawn more agents, and stop if cost, permissions or incomplete evidence become problematic.

## Research contract for every worker

Return role, as-of date/IST, consulted source URL/document and publication timestamp, factual observations and exact units, assumptions separate from facts, counter-evidence, unresolved data gaps, private-data handling note, any actual program commands and hashes, and one concise recommendation for human review.

The Lead reconciles consolidated vs standalone statements, share-count revisions, FY vs quarter, lakhs vs crores, source release versus ingestion timing, and corporate actions. Do not average incompatible figures. Keep alternate hypotheses when conflicts cannot be resolved.

## Control gates

- Explicit user authorization for past chat/memory/connected apps, private portfolio data and any expensive or external tools. Share minimum needed context with agents; no copying private records to unauthorized workers.
- Bounded maximum **six agents**, no indefinite loops, no hidden credentials or automated broker orders.
- Where provenance, adjustment or point-in-time validity is unavailable: mark NOT VERIFIED and ABSTAIN on actionable forecasts.
- Before sign-off: strongest contradictory case and source-quality review from an independent skeptic.
- Distinguish researcher accuracy and evidence coverage from predictive alpha. No accuracy guarantees.

## After installation

The installing agent proactively offers **three usable context-specific starting prompts**, based only on the current conversation and other sources it is authorized and genuinely able to access. Example for banks/NBFC: "Compare recent GNPA/NNPA, slippages, credit costs and valuation with linked filings for two lenders I specify." Example for portfolio research: "Audit a de-identified portfolio for concentration, drawdown and hidden assumptions." If no past context is available, offer generic prompts and ask which research task takes longest. Do not pretend to remember missing personal history.
