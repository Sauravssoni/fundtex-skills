---
name: fundtex-india-diligence
description: Institutional India fundamental equity and bank/NBFC analyst workflow, source-linked company filings, cashflow quality, working capital, leverage, GNPA/NNPA/NIM/CRAR/CET1, valuation scenario review and audited research packet. Use for Indian equity research, due diligence, valuation preparation and investment committee briefing.
argument-hint: "[Indian issuer, NSE/BSE ticker, authorized filing or financial JSON]"
---

# Fundtex India Diligence — Financial Analyst Desk

**Fundtex Financial Intelligence, Syntheon Technology Private Limited.** Operational guidance and a reproducible arithmetic tool, not proof of a current exchange-data terminal or trading advice.

## First action

Determine if the user wants issuer due diligence, comparison, lender financials or an investment-committee memo. Check relevant, accessible user context (never claim past-chat access if unavailable) and confirm company identity, NSE/BSE ticker, dates and period. For public information, prioritize actual NSE/BSE issuer filings and the company's official investor relations disclosures; cite only sources genuinely opened. Link a full report or provide a concrete research result, not a generic financial glossary.

## Use the validated calculator

1. Inspect docs/COMPANY_DILIGENCE.md, docs/INDIA_RESEARCH_DESK.md and docs/CLAUDE_FIRST_RUN.md if first installation.
2. For a working, explicitly fictional demonstration:

       python3 -m fundtex_india.cli diligence --inputs examples/india_company_diligence_SYNTHETIC.json --format markdown
       python3 -m fundtex_india.cli diligence --inputs examples/india_bank_diligence_SYNTHETIC.json --format markdown

3. For a real listed company, obtain authorized current and comparable period figures from dated filings. Record issuer name, ticker/ISIN, consolidated vs standalone basis, INR/crore/lakh units, fiscal period and source publication timestamp. Transcribe figures into the documented JSON input with actual source titles and links; NEVER invent unobserved values. Every externally sourced URL remains marked not independently verified by the calculation engine.
4. Run fundtex diligence --inputs /authorized/company.json --format markdown, or the equivalent Python module if the launcher is not on PATH.
5. Inspect ratio questions and challenge the assumed accounting economics using the source filings, industry structure, liquidity and conflicting evidence. Distinguish calculated arithmetic from verified authenticity.

## Domain-specific rigor

For nonfinancial issuers: operating cash flow relative to net income; receivable intensity; working capital, one-offs, balance sheet debt/net debt, EBITDA, interest coverage, capex/FCF, management commentary, governance, dilution and sector risk.

For banks/NBFCs: GNPA, NNPA, slippages when explicitly sourced, NIM, credit costs, provisions, CET1/CRAR, capital quality, liquidity/ALM and lending economics. Do NOT treat generic industrial EV/EBITDA as the default bank valuation metric.

## Output

Executive thesis and biggest concern, dated primary evidence ledger, correctly scaled financials, forensic indicators and uncertainty, strongest counterargument, bull/base/bear assumptions, identified data gaps and a concise analyst-review checklist. If any fact is unavailable, label it NOT VERIFIED; if a directional market advantage is unproven, abstain from actionable price predictions.

## Fallbacks

No verified price feed? Continue fundamental/source diligence and clearly flag absent market prices. No permitted data? Show fictional demonstration as such and ask for an actual approved filing. No subagents? Work sequentially. No independent predictive benchmark? Do not claim 11/10 investment performance or guaranteed returns. Never send confidential employer/client records to external tools without authorization.
