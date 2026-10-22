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
from .http import fetch_bytes

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
    blob = json.loads(fetch_bytes(url, max_bytes=5_000_000, headers={"User-Agent": "Mozilla/5.0 FundtexResearch/0.1"}))
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


def yahoo_ohlcv_prices(symbol: str, *, range_: str = "2y", interval: str = "1d") -> dict:
    """Actual unadjusted Yahoo quote OHLCV, NOT fabricated from adjusted close.

    This is a public, unofficial, potentially delayed/non-tradable history.
    Corporate actions, holidays, price consistency, exchange identity and
    redistribution rights require independent verification. Never substitute
    adjusted close for the raw OHLC close: that mixes incompatible price bases.
    """
    symbol=validate_symbol(symbol)
    if range_ not in {"1mo","3mo","6mo","1y","2y","5y"} or interval!="1d":
        raise ValueError("Public OHLC research requires supported daily range")
    url="https://query1.finance.yahoo.com/v8/finance/chart/"+urllib.parse.quote(symbol)+"?"+urllib.parse.urlencode({"range":range_,"interval":interval})
    blob=json.loads(fetch_bytes(url,max_bytes=5_000_000,headers={"User-Agent":"Mozilla/5.0 FundtexResearch/0.1"}))
    chart=blob.get("chart") or {}
    if chart.get("error"):
        raise ValueError("OHLC provider reported an error")
    result=chart.get("result") or []
    if len(result)!=1:
        raise ValueError("Public chart provider returned no unique instrument")
    entry=result[0]
    response_symbol=(entry.get("meta") or {}).get("symbol")
    if response_symbol and response_symbol.upper()!=symbol:
        raise ValueError("Provider returned different ticker; refused")
    quotes=(entry.get("indicators") or {}).get("quote") or []
    if len(quotes)!=1 or not isinstance(quotes[0],dict):
        raise ValueError("OHLC provider returned malformed quote series")
    items=quotes[0]
    timestamps=entry.get("timestamp") or []
    if not isinstance(timestamps,list) or not 12<=len(timestamps)<=20000:
        raise ValueError("OHLC provider requires 12..20000 actual dated timestamps")
    bars=[]
    omitted=0
    for i,ts in enumerate(timestamps):
        values=[]
        for k in ("open","high","low","close"):
            seq=items.get(k)
            if not isinstance(seq,list):
                raise ValueError("Provider did not supply genuine open/high/low/close series")
            values.append(seq[i] if i<len(seq) else None)
        if any(x is None for x in values):
            omitted+=1
            continue
        if any(isinstance(x,bool) or not isinstance(x,(int,float)) for x in values):
            raise ValueError("Non-numeric OHLC candle returned")
        o,h,l,c=map(float,values)
        if any(not math.isfinite(x) or x<=0 for x in (o,h,l,c)):
            raise ValueError("Nonfinite or nonpositive provider OHLC")
        if l>min(o,c) or h<max(o,c) or h<l:
            raise ValueError("Provider OHLC constraints violated; no phantom candles")
        seq=items.get("volume") or []
        vol=seq[i] if i<len(seq) else None
        if vol is not None and (isinstance(vol,bool) or not isinstance(vol,(int,float)) or
                                 not math.isfinite(vol) or vol<0):
            raise ValueError("Provider volume invalid")
        day=dt.datetime.fromtimestamp(ts,tz=dt.timezone.utc).date().isoformat()
        bars.append({"date":day,"open":o,"high":h,"low":l,"close":c,"volume":vol})
    if len(bars)<12:
        raise ValueError("Not enough actual public OHLC candles: no invented backfill")
    bars.sort(key=lambda x:x["date"])
    validate_rows(bars)  # Duplicates/future dates/close-volume validity.
    return {"symbol":symbol,"rows":bars,"source":url,
            "observed_as_of":bars[-1]["date"],
            "quality":"UNOFFICIAL_UNADJUSTED_OHLC_NOT_EXCHANGE_VERIFIED",
            "omitted_incomplete_provider_candles":omitted,
            "adjustment_basis":"RAW_UNADJUSTED_QUOTES_ONLY",
            "note":"Best-effort Yahoo raw OHLC; publisher rights, adjustment, exchange timestamp and splits NOT verified; not a live or licensed exchange feed."}
