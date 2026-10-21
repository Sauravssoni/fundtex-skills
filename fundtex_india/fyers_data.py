"""FYERS official API v3: opt-in free-to-eligible-client read-only market data.

No order API, no credentials stored, no guessed NSE identifiers, no redirects.
Official documentation: https://fyers.in/api-docs/v3/api/market-data/
"""
from __future__ import annotations
import datetime as dt
import math
import os
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
from .market import validate_symbol,validate_rows
from .broker_quotes import _request,_quote,_extract_ltp

def configured():
    return bool(os.getenv("FUNDTEX_FYERS_APP_ID") and os.getenv("FUNDTEX_FYERS_ACCESS_TOKEN"))

def _auth():
    app=os.getenv("FUNDTEX_FYERS_APP_ID")
    token=os.getenv("FUNDTEX_FYERS_ACCESS_TOKEN")
    if not app or not token:
        raise ValueError("FYERS app ID/access token not configured; no market data retrieved")
    return {"Authorization":app+":"+token,"Accept":"application/json"}

def _symbol(symbol):
    sym=validate_symbol(symbol)
    if not sym.endswith(".NS"):
        raise ValueError("FYERS automatic symbol mapping currently supports .NS equity symbols only; BSE needs a verified instrument master")
    return "NSE:"+sym[:-3]+"-EQ"

def parse_quote(payload,symbol):
    sym=validate_symbol(symbol);original=_symbol(sym)
    if payload.get("s")!="ok" or payload.get("code") not in (None,200):
        raise ValueError("FYERS quote provider reported an error")
    items=payload.get("d")
    if not isinstance(items,list):raise ValueError("Malformed FYERS quote response")
    exact=[x for x in items if isinstance(x,dict) and x.get("n")==original and x.get("s")=="ok"]
    if len(exact)!=1 or not isinstance(exact[0].get("v"),dict):
        raise ValueError("FYERS quote for requested instrument missing")
    fields=exact[0]["v"]
    observed=fields.get("tt")
    if observed is not None and observed!=0:
        try:
            observed=dt.datetime.fromtimestamp(int(observed),tz=dt.timezone.utc).isoformat()
        except (ValueError,TypeError,OverflowError,OSError):
            observed=None
    else:observed=None
    return _quote(_extract_ltp(fields.get("lp")),sym,"fyers",observed,
                  "FYERS official authenticated quote REST snapshot, client-entitled data, not continuous streaming")

def quote(symbol):
    sym=validate_symbol(symbol)
    url="https://api-t1.fyers.in/data/quotes?"+urlencode({"symbols":_symbol(sym)})
    response=_request(url,_auth())
    return parse_quote(response,sym)

def parse_history(payload,symbol):
    sym=validate_symbol(symbol)
    if payload.get("s")!="ok" or payload.get("code") not in (None,200):
        raise ValueError("FYERS historical provider reported an error")
    candles=payload.get("candles")
    if not isinstance(candles,list) or len(candles)>1000:
        raise ValueError("Malformed/oversized FYERS candles")
    rows=[]
    for candle in candles:
        if not isinstance(candle,(list,tuple)) or len(candle)<6:
            raise ValueError("Invalid FYERS candle")
        when=dt.datetime.fromtimestamp(int(candle[0]),tz=dt.timezone.utc).astimezone(ZoneInfo("Asia/Kolkata")).date()
        open_,high,low,close,volume=map(float,candle[1:6])
        if any(not math.isfinite(v) for v in (open_,high,low,close,volume)):
            raise ValueError("Non-finite FYERS OHLCV")
        if not (low<=open_<=high and low<=close<=high and close>0 and open_>0 and volume>=0):
            raise ValueError("Invalid FYERS OHLCV range")
        rows.append({"date":when.isoformat(),"open":open_,"high":high,"low":low,"close":close,"volume":volume})
    rows.sort(key=lambda r:r["date"])
    # Existing source validator checks date duplicates, future observations and close.
    validate_rows(rows)
    if len(rows)<12:raise ValueError("Insufficient real FYERS historical candles")
    return {"symbol":sym,"rows":rows,"observed_as_of":rows[-1]["date"],
            "quality":"AUTHENTICATED_FYERS_HISTORY_NOT_TICK_STREAM",
            "source":"https://api-t1.fyers.in/data/history",
            "note":"Client-authorized FYERS daily OHLCV; adjust for corporate actions as independently verified; no guaranteed source redistribution rights"}

def history(symbol,*,range_="1y",interval="1d"):
    sym=validate_symbol(symbol)
    if interval!="1d" or range_ not in ("1mo","3mo","6mo","1y"):
        raise ValueError("FYERS reader supports at most 1 year of daily candles per request")
    days={"1mo":35,"3mo":100,"6mo":188,"1y":364}[range_]
    today=dt.datetime.now(ZoneInfo("Asia/Kolkata")).date()
    start=today-dt.timedelta(days=days)
    query={"symbol":_symbol(sym),"resolution":"D","date_format":"1",
           "range_from":start.isoformat(),"range_to":today.isoformat(),"cont_flag":"1"}
    url="https://api-t1.fyers.in/data/history?"+urlencode(query)
    response=_request(url,_auth())
    return parse_history(response,sym)
