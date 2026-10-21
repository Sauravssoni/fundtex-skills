# Fundtex Analyst Studio v0.9 — Interactive Charts, Exports and Evidence

The public CLI can turn a dated, authorized user CSV into a self-contained interactive chart, source-hashed SVG, annotated historical reference levels, CSVs, a Markdown research note, and an optional XLSX/PDF/PNG report pack.

**CRITICAL:** Chart refresh is from ONE approved local CSV on localhost, NOT licensed live NSE/BSE quotes. No current real-time market feed, exchange brokerage or Bloomberg-like data service is implied.

## Starter commands

    python3 -m fundtex_india.cli chart --csv examples/india_prices.csv --symbol RELIANCE.NS --out /tmp/chart.html
    python3 -m fundtex_india.cli chart --csv examples/india_prices.csv --symbol RELIANCE.NS --format svg --out /tmp/chart.svg
    python3 -m fundtex_india.cli analyst-pack --csv examples/india_prices.csv --symbol RELIANCE.NS --out /tmp/new-analyst-report
    python3 -m fundtex_india.cli chart-serve --csv examples/india_prices.csv --symbol RELIANCE.NS --port 8734

The example CSV contains SYNTHETIC_FIXTURE closing prices, NOT historical Reliance pricing. A close-only file generates a line chart. Candlesticks are only drawn from actual supplied date,open,high,low,close OHLC rows. The source must have strictly increasing dates, no future rows and valid high/low/volume.

For annotations supply --annotations /approved/annotations.json with an array of objects:
- level: {"type":"level","price":125.5,"label":"Manual reference"}
- zone: {"type":"zone","low":120,"high":124,"label":"Visual band"}
- callout: {"type":"callout","date":"2026-02-03","price":128,"label":"Reviewed event"}

HTML drawing tools offer manual levels, clear, export PNG, export SVG and export annotation JSON. Drawings and SMA crossings are HISTORICAL descriptive observations, not empirically validated trade signals.

## Portfolio / visual tools

Provide an approved holdings.csv; optional aligned portfolio-prices.csv produces sector allocation, portfolio weight bars and real historical correlation heatmaps. Do not infer correlations from weights. Generic visuals accept approved JSON and create static SVG:

    fundtex visual --kind pie --inputs /approved/sector-weights.json --out /new/sector.svg
    fundtex visual --kind bar --inputs /approved/peer-metrics.json --out /new/bars.svg
    fundtex visual --kind heatmap --inputs /approved/correlations.json --out /new/heatmap.svg
    fundtex visual --kind waterfall --inputs /approved/valuation-bridge.json --out /new/waterfall.svg
    fundtex visual --kind histogram --inputs /approved/return-samples.json --out /new/histogram.svg

## Excel, PDF and screenshot support

The default installer stays dependency-light. Optional workbook requires vetted artifact_tool, PDF memo requires ReportLab, chart browser PNG screenshot requires installed Playwright and compatible Chromium. Do not silently install packages in a user's global Python. When absent, manifest.json MUST disclose omitted optional artifacts while preserving source-auditable SVG/HTML/CSV/Markdown.

An XLSX workbook, when supported, contains Executive, Price History, Indicators, Historical Events, Sources and Limits. It uses dated inputs and auditable daily-return formulas; synthetic data never becomes a real issuer statement.

## Rules

- Source hashes indicate input identity, NOT authenticity or licensed distribution rights.
- Never overwrite an existing output file/folder. Preserve original dates and data classification.
- Never automatically access a private employer's portfolio or conversation history.
- No autonomous trades, recommendations, validated predictive alpha or source verification by reading a skill.
- Check file existence and quality, show source gaps and opposing hypotheses, obtain analyst review.

## Tests

    python3 -m unittest -v tests.test_fundtex_studio
    python3 -m unittest discover -s tests -p 'test_fundtex*.py' -v

Prioritize the first useful chart and report over expensive synthetic simulations. The optional million-path numerical gate tests computation only and not real-market profitability.
