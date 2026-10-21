# India Company Diligence — fundamental analyst workflow

Fundtex's diligence engine converts **your own approved, manually transcribed** issuer data into a structured, auditable screening memo. It is useful for checking ratio arithmetic, working capital, cash-conversion divergence and lender asset-quality trends. It is NOT a live filings ingestion connector, independent auditor or Bloomberg replacement.

## Fast offline demonstration

    python3 -m fundtex_india.cli diligence --inputs examples/india_company_diligence_SYNTHETIC.json --format markdown
    python3 -m fundtex_india.cli diligence --inputs examples/india_bank_diligence_SYNTHETIC.json --format json

These are invented financial figures, not real Indian listed companies. They deliberately contain questions to ask (e.g. cash flow versus profits) and demonstrate sector-specific bank/NBFC fields. Do not copy their values into real analyst reports or suggest the price ticker actually exists.

## To run on an actual company

1. Obtain an issuer's latest results and annual reports from **actually opened, dated NSE/BSE filings or the official issuer investor relations site**. Confirm authorized use and whether figures are consolidated or standalone.
2. Manually map the exact period, INR unit (rupees/lakh/crore), sector and current / comparable previous periods into a JSON object. Missing source data stays missing—don't fill the gaps from assumptions.
3. Put at least one actual title, date and HTTPS URL in the source list; the engine flags them as USER_CITED_NOT_INDEPENDENTLY_VERIFIED because it cannot authenticate URLs.
4. Run Fundtex diligence on that locally approved file and reproduce calculated ratios. Keep original filings available for independent review.
5. Ask Claude/Codex to compare the ratio checks against original disclosures, evaluate inconsistencies, make a bull/bear/unknown investment research case, and identify information gaps.

## Example schema (fictional only)

    {
      "company": {"name": "ILLUSTRATIVE CO (FICTIONAL)", "symbol": "DEMO.NS", "sector": "manufacturing"},
      "fiscal_period": "FY2026 illustrative",
      "currency": "INR",
      "unit": "crore",
      "data_quality": "SYNTHETIC_FIXTURE",
      "sources": [],
      "current": {"revenue": 1500, "net_income": 140, "operating_cash_flow": 42, "capital_expenditure": 110, "gross_debt": 750, "cash_equivalents": 100, "ebitda": 140, "receivables": 675},
      "previous": {"revenue": 1200}
    }

All input fields are optional except identity, period, currency, units and at least one current metric. Unknown fields fail closed. The lender class supports GNPA%, NNPA%, NIM%, credit-cost%, CRAR%, CET1% and provision-coverage% with period change in percentage points. Do not interpret generic EBITDA metrics as suitable banking valuation methods.

## Deliverable

- Symbol/sector, reporting period and data quality.
- Calculated reported-data ratios in consistent INR units.
- Explicit questions about negative free cash flow, poor cash conversion, receivables or leverage when formula thresholds are met.
- Lender-specific capital quality, asset-quality, interest-margin trends when inputs are available.
- Missing metrics, original filing URLs and dates **without falsely calling them independently verified**.
- Analyst's next validation steps and reviewer approval, with no automated recommendation.

## Boundaries

Do not give proprietary client financial statements or research models to a third-party host without employer approval. A correctly calculated ratio cannot detect manipulated accounting or validate issuer figures. No automated data ingestion, exchange feed, future prediction or actual investment recommendation is implied.
