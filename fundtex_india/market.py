"""Validated market-data input. Only labelled, sourced prices; never synthetic live quotes."""
from __future__ import annotations
import csv
import datetime as dt
import json
import math
import re
import urllib.parse
import urllib.request
from pathlib import Path

SYMBOL = re.compile(r"^[A-Z0-9][A-Z0-9&_-]{0,24}\.(NS|BO)$")

def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not SYMBOL.fullmatch(symbol):
        raise ValueError("Use an NSE symbol ending .NS or BSE symbol ending .BO, e.g. INFY.NS")
    return symbol

def _date(value: str) -> dt.date:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date()

def validate_rows(rows: list[dict]) -> list[dict]:
    if len(rows) < 2:
        raise ValueError("At least two observations required")
    out, seen = [], set()
    for row in rows:
        day = _date(str(row.get("date") or row.get("timestamp") or ""))
        if day in seen:
            raise ValueError(f"Duplicate observation date: {day}")
        seen.add(day)
        close = float(row["close"])
        if not math.isfinite(close) or close <= 0:
            raise ValueError("Closing prices must be finite and strictly positive")
        volume = row.get("volume")
        if volume not in (None, ""):
            volume = float(volume)
            if not math.isfinite(volume) or volume < 0:
                raise ValueError("Volume cannot be negative or nonfinite")
        out.append({"date": day.isoformat(), "close": close, "volume": volume})
    out.sort(key=lambda x: x["date"])
    if out[-1]["date"] > dt.datetime.now(dt.timezone.utc).date().isoformat():
        raise ValueError("Future observation detected")
    return out

def csv_prices(path: str, symbol: str | None = None) -> dict:
    p = Path(path)
    with p.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "close" not in reader.fieldnames or not ({"date", "timestamp"} & set(reader.fieldnames)):
            raise ValueError("CSV needs date or timestamp and close columns")
        all_rows = list(reader)
    if symbol:
        symbol = validate_symbol(symbol)
        if "symbol" in reader.fieldnames:
            all_rows = [x for x in all_rows if x.get("symbol", "").strip().upper() == symbol]
    if not all_rows:
        raise ValueError("No observations for requested symbol")
    rows = validate_rows(all_rows)
    import hashlib
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    return {"symbol": symbol, "rows": rows, "source": f"csv:{p.name}", "sha256": digest,
            "observed_as_of": rows[-1]["date"], "quality": "USER_SUPPLIED_UNVERIFIED",
            "note": "CSV content and adjustments must be verified by an analyst; not a live exchange feed."}

def yahoo_prices(symbol: str, *, range_: str = "1y", interval: str = "1d") -> dict:
    symbol = validate_symbol(symbol)
    if range_ not in {"1mo", "3mo", "6mo", "1y", "2y", "5y"} or interval not in {"1d", "1wk"}:
        raise ValueError("Unsupported chart query")
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(symbol) + "?" + urllib.parse.urlencode({"range": range_, "interval": interval})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 FundtexResearch/0.1"})
    with urllib.request.urlopen(req, timeout=12) as response:
        blob = json.load(response)
    chart = blob.get("chart") or {}
    if chart.get("error"):
        raise ValueError(f"Chart provider error: {chart['error']}")
    results = chart.get("result") or []
    if not results:
        raise ValueError("Chart provider returned no data; no price was inferred")
    entry = results[0]
    quotes = entry["indicators"]["quote"][0]
    adj = (entry["indicators"].get("adjclose") or [{}])[0].get("adjclose")
    closes = adj if adj else quotes.get("close", [])
    rows = []
    for i, ts in enumerate(entry.get("timestamp") or []):
        c = closes[i] if i < len(closes) else None
        if c is None:
            continue
        rows.append({"date": dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).date().isoformat(),
                     "close": c, "volume": (quotes.get("volume") or [None] * len(closes))[i]})
    return {"symbol": symbol, "rows": validate_rows(rows), "source": url,
            "observed_as_of": rows[-1]["date"] if rows else None,
            "quality": "UNOFFICIAL_BEST_EFFORT_DELAYED",
            "note": "Unofficial provider; availability, adjustment, timeliness and usage rights are not guaranteed. Not exchange-licensed data."}
