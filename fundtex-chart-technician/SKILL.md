---
name: fundtex-chart-technician
description: Audited India equity chart generation with optional OHLC candlesticks, historical SMA/RSI, manual annotations, screenshots, source hashes and local CSV-refresh viewer.
---
# Fundtex Chart Technician
Never invent live NSE/BSE prices or OHLC. Validate source, rights, date, symbol and corporate actions. Use fundtex chart --csv /approved/prices.csv --symbol INFY.NS --out /new/chart.html for interactive browser charts, or --format svg for vector graphics. Add optional --annotations notes.json for marked levels, zones and callouts. fundtex chart-screenshot --html chart.html --out /new/chart.png requires an approved Chromium/Playwright runtime; HTML itself offers browser PNG/SVG export. fundtex chart-serve --csv /approved/prices.csv --symbol INFY.NS refreshes one local file on 127.0.0.1:8734; this is NOT exchange live streaming. Treat any historical SMA crossings as descriptive and do not claim predictive alpha.

## Evidence gates

- Verify source dates, whether file was genuinely published, and any dividend or split adjustments.
- Confirm a real OHLC file before rendering candlesticks, otherwise render close-only lines.
- Use user-authorized browser tools; no hidden third-party charting upload.
- Deliver a source receipt, clear uncertainty and a human-review action.
