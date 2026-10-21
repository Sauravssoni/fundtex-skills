# India Market Data — Provenance-First Imports

Fundtex does NOT silently scrape NSE/BSE or redistribute market data. Analysts supply locally held, authorized datasets.

## NSE UDiFF exchange ZIPs

Reference: https://www.nseindia.com/all-reports and https://www.nseindia.com/static/resources/forms-formats-members .

Collect official-format CM UDiFF ZIP archives for your intended dates subject to NSE licensing and authorization. Import two or more through the local command:

    python3 -m fundtex_india.cli import --source-type nse-udiff --files /approved/day1.zip /approved/day2.zip --symbol INFY.NS --out /tmp/infy-unadjusted.csv

The parser reads the UDiFF capital market columns TradDt, TckrSymb, SctySrs, ClsPric, ISIN, TtlTradgVol, filters only EQ, rejects duplicates/mismatched ISIN, refuses oversized files, and saves input SHA-256 hashes in a manifest. It never extracts ZIP entries to disk.

IMPORTANT: UDiFF closes are unadjusted for corporate actions/dividends. The importer verifies file *shape*, NOT exchange authenticity, redistribution rights, or total-return adjustments.

## Archived Google Finance-style CSV

    python3 -m fundtex_india.cli import --source-type googlefinance --files /approved/research.csv --symbol RELIANCE.NS --out /tmp/reliance.csv

Input fields: Date,Close with optional Open,High,Low,Volume, as historic Google Finance exports. Dates can be US-format month/day/year. Inputs are unverified third-party historic records and should never be represented as today's official prices.

## Research protocols

    python3 -m fundtex_india.cli forecast --csv /tmp/reliance.csv --symbol RELIANCE.NS --window 252 --margin 0.1
    python3 -m fundtex_india.cli godeye --csv /tmp/reliance.csv --symbol RELIANCE.NS --min-train 120 --train-lookback 60 --cost-bps 12

Forecast LAB produces past-only historical up-frequency, one-day 10th/50th/90th return quantiles, subsequent-outcome Brier scores, historical interval coverage, benchmark comparisons, moving-block bootstrap and explicit abstention gates. This is NOT a validated probability of profitability or a client recommendation.

GOD EYE is a separate four-strategy trailing performance selector; it does not use real fee schedules, actual next-open fills, corporate actions, point-in-time universes or security-level fundamentals, and therefore cannot certify backtest alpha.

The generated CSV is created exclusively without overwriting an existing path. Adjacent manifest includes SHA-256 of all input files; neither dataset nor manifest is transmitted automatically to third-party services. Use only institution-authorized datasets.
