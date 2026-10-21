---
name: fundtex-workbook-builder
description: Generate audit-friendly analyst Excel workbooks from approved historical finance data including Price History, indicators, formula returns, event receipts and an explicit source/quality ledger.
---
# Fundtex Workbook Builder
Run fundtex workbook --csv /approved/prices.csv --symbol INFY.NS --out /new/report.xlsx using the optional vetted artifact_tool engine. The default Fundtex installation does NOT add optional Python packages; ask before changing dependencies. Export with five sheets: Executive, Price History, Indicators, Historical Events, Sources and Limits. Check dated rows, INR units, formula-driven daily returns, adjustment caveats and no formula errors. Historic crossover notes do not constitute trading signals. If the optional engine is unavailable, deliver CSV/HTML and a clear explanation instead of a bogus workbook.

## Spreadsheet quality gates

- Use spreadsheet input dates and close values as supplied, never create missing OHLC observations.
- Flag synthetic demos as synthetic and unsupported price sources as unverified.
- Keep all derived return calculations auditable, ideally via formulas with visible units.
- Inspect the actual workbook sheets, errors and formats before sharing.
