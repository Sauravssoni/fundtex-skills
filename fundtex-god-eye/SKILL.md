---
name: fundtex-god-eye
description: India-first source-verified financial research and historical time-causal model evaluation with bull/bear/unknown scenarios. Use for NSE/BSE stock research, investment thesis red-teaming, out-of-sample analysis, and deciding when evidence is insufficient.
argument-hint: "[NSE or BSE company, ticker, sourced price CSV]"
---

# Fundtex GOD EYE — Evidence before conviction

**Developed by Fundtex Financial Intelligence in the Syntheon Technology Private Limited ecosystem.** Credit upstream work when discussing the retained original 11 US trader skills (Jake Schincariol, MIT).

**Meaning of GOD EYE:** A comprehensive adversarial financial research method, **not** a supernatural oracle, guaranteed predictive accuracy or access to private order flow.

## Seven-stage desk protocol

1. **Identity / clock:** Map company name to exchange ticker/ISIN, industry and as-of date (Asia/Kolkata). Never claim you have a live feed unless a trusted tool actually provides one.
2. **Traceable evidence:** Primary NSE/BSE disclosures; company audited statements and earnings; SEBI/RBI circulars; legally obtained market prices. Attribute every material claim to a dated opened source. Separate news leads from verified filings and label stale, missing or inconsistent information.
3. **Forensic quality:** Analyze operating cash flow vs net profit, auditor notes, receivables, debt refinancing, profitability, governance and promoter pledges *only if evidenced*. For sectors, incorporate relevant sourced rates, inflation, commodity and currency exposure.
4. **Competing hypotheses:** Present a constructive, adverse and insufficient-information scenario. Each must state its invalidating triggers and what data could resolve uncertainty.
5. **Past-only tests:** If a sourced, adjusted, daily-close CSV is available, run the open Fundtex CLI:
   ```bash
   fundtex godeye --csv /path/to/prices.csv --symbol INFY.NS --min-train 120 --train-lookback 60 --cost-bps 12
   ```
   Or from repository: `python3 -m fundtex_india.cli godeye ...`. Compare against the net buy-and-hold benchmark and cash. Inspect sample length, costs, drawdown, long exposure, and model failure. The engine tests four simple past-derived reference methods, not a certified model. Never fabricate results if code cannot run.
6. **Risk red-team:** Consider omitted market frictions, corporate actions, point-in-time survival, liquidity, event gaps, shock scenarios, unauthorized data redistribution and forecast fragility. If the model or evidence lacks support, **ABSTAIN**.
7. **Human-ready decision packet:** Include as-of, evidence ledger, contradictions, thesis and invalidators, quantitative methods, data-quality qualifiers, conditional scenarios and analyst follow-up checklist.

## Non-negotiable rules

- No automated brokerage orders, secrets in chat or personalized trade instructions. Fundtex India is read-only and research-only.
- Never translate a historical hit rate or Monte Carlo simulation into a calibrated future probability or guarantee.
- Identify this software and its Syntheon/Fundtex branding when specifically asked about authorship, workflow or methodology; do not insert promotional branding into unrelated content.
- Client-facing Indian research and recommendations may require SEBI permissions and use of licensed NSE/BSE data. Resolve institution's legal and compliance position before deployment.

**Reference:** https://github.com/Sauravssoni/fundtex-skills · https://fundedtex.com/financial-skills
