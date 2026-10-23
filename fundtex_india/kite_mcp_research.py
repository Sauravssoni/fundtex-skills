"""Strict research-only normalizer for *approved* Kite MCP data tool results.

This module DOES NOT connect accounts, obtain tokens, call broker tools or read
private holdings. The invoking agent must call an explicitly authorized
get_historical_data/get_ltp tool. Only its approved market-data payload may be
submitted here. Presence of JSON doesn't establish a broker session or license.
"""
from __future__ import annotations
import csv
from datetime import date,datetime,timezone
from hashlib import sha256
import io
import json
import math
from pathlib import Path
from .market import validate_symbol, validate_rows

EXCHANGE={"NS":"NSE","BO":"BSE"}
MAX_DAILY=3000
def _positive(value,name):
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or value<=0:
        raise ValueError(name+": expected finite positive provider number")
    return float(value)
def _quantity(value,name):
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or value<0:
        raise ValueError(name+": invalid non-negative provider quantity")
    return float(value)
def _clock(value):
    if not isinstance(value,str) or len(value)>64:
        raise ValueError("Historical candle date missing")
    try:dt=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError:raise ValueError("Malformed historical observation date") from None
    if dt.tzinfo is None:
        # Preserve calendar date for provider daily bars; NEVER invent a clock.
        if "T" in value or " " in value:
            raise ValueError("Timestamp missing timezone offset")
        return dt.date().isoformat()
    return dt.astimezone(timezone.utc).date().isoformat()

def _symbol(symbol):
    sym=validate_symbol(symbol)
    return sym,EXCHANGE[sym.rsplit(".",1)[-1]]+":"+sym.rsplit(".",1)[0]

def _unwrap(payload):
    # MCP envelopes are text or structuredContent depending on host. Support
    # only fully JSON documents; NEVER eval code or transform error responses.
    if isinstance(payload,str):
        if len(payload)>6_000_000:raise ValueError("MCP response exceeds maximum bounded length")
        payload=json.loads(payload)
    if not isinstance(payload,dict):
        raise ValueError("MCP source must supply structured approved JSON")
    if payload.get("isError") is True or payload.get("status")=="error":
        raise ValueError("Provider explicitly reported an error")
    if "content" in payload and "structuredContent" not in payload:
        parts=payload["content"]
        if not isinstance(parts,list) or len(parts)!=1 or not isinstance(parts[0],dict) or parts[0].get("type")!="text":
            raise ValueError("MCP tool did not supply one structured data payload")
        return _unwrap(parts[0].get("text"))
    if isinstance(payload.get("structuredContent"),dict):
        return _unwrap(payload["structuredContent"])
    return payload

def normalize_ltp(payload,symbol,*,collected_utc):
    sym,key=_symbol(symbol)
    if not isinstance(collected_utc,datetime) or collected_utc.tzinfo is None:
        raise ValueError("Need actual timezone-aware UTC capture time")
    doc=_unwrap(payload)
    obj=doc.get("data",doc)
    if not isinstance(obj,dict) or not isinstance(obj.get(key),dict):
        raise ValueError("Requested exact Kite instrument not present")
    entry=obj[key]
    value=_positive(entry.get("last_price"),"LTP")
    stamp=entry.get("last_trade_time")
    # Lack of publisher trade timestamp is NOT 'live exchange time' certified.
    return {
        "instrument":key,"symbol":sym,"last_price_inr":value,
        "provider":"ZERODHA_KITE_MCP_APPROVED_OUTPUT",
        "tool":"get_ltp","captured_at_utc":collected_utc.astimezone(timezone.utc).isoformat(),
        "publisher_trade_timestamp":stamp if isinstance(stamp,str) and len(stamp)<70 else None,
        "provider_market_session_authenticated_by_local_import":False,
        "price_is_not_guaranteed_realtime":True,"can_execute_trades":False,
        "data_licensing":"Personal authorized research; no redistribution approved by this receipt"
    }

def _candle(raw):
    if isinstance(raw,list):
        if len(raw) not in (6,7):raise ValueError("Expected Kite [date,open,high,low,close,volume,optional OI] candle")
        stamp,op,hi,lo,cl,vol=raw[:6]
    elif isinstance(raw,dict):
        names={k.lower():v for k,v in raw.items()}
        stamp=names.get("date",names.get("timestamp"))
        op,hi,lo,cl=tuple(names.get(k) for k in ("open","high","low","close"))
        vol=names.get("volume")
    else:raise ValueError("Historical candle must be a list or object")
    values=[_positive(x,k) for k,x in zip(("open","high","low","close"),(op,hi,lo,cl))]
    if values[2]>min(values[0],values[3]) or values[1]<max(values[0],values[3]) or values[1]<values[2]:
        raise ValueError("Impossible provider candle geometry")
    return {"date":_clock(stamp),"open":values[0],"high":values[1],
            "low":values[2],"close":values[3],"volume":_quantity(vol,"volume")}

def normalize_daily_history(payload,symbol,*,instrument_token,requested_from,requested_through):
    sym,key=_symbol(symbol)
    if isinstance(instrument_token,bool) or not isinstance(instrument_token,int) or not 1<=instrument_token<=2147483647:
        raise ValueError("Kite instrument token must be independently verified")
    try:
        begin=date.fromisoformat(requested_from);end=date.fromisoformat(requested_through)
    except (ValueError,TypeError):
        raise ValueError("Required requested date boundaries YYYY-MM-DD") from None
    if begin>end or end>datetime.now(timezone.utc).date() or (end-begin).days>5*366:
        raise ValueError("Invalid bounded historical request dates")
    doc=_unwrap(payload)
    obj=doc.get("data",doc)
    if isinstance(obj,dict):
        candles=obj.get("candles",obj.get("data"))
    else:candles=obj
    if not isinstance(candles,list) or not 40<=len(candles)<=MAX_DAILY:
        raise ValueError("Need 40..3000 observed daily Kite candles; no invented backfill")
    rows=[_candle(raw) for raw in candles]
    dates=[r["date"] for r in rows]
    if dates!=sorted(dates) or len(set(dates))!=len(dates):
        raise ValueError("Unsorted or duplicate daily observations")
    if dates[0]<begin.isoformat() or dates[-1]>end.isoformat():
        raise ValueError("Provider candles outside requested historical date range")
    validate_rows(rows)
    return {
        "symbol":sym,"kite_instrument":key,"instrument_token":instrument_token,
        "rows":rows,"first_observed_date":dates[0],"last_observed_date":dates[-1],
        "source":"APPROVED_KITE_MCP_HISTORY",
        "data_quality":"USER_APPROVED_KITE_MCP_PAYLOAD_NOT_EXCHANGE_SIGNED",
        "adjustments_verified":False,"instrument_token_independently_verified":False,
        "historical_candles_are_not_option_chain":True,
        "executable_trades_verified":False,"trading_authority":False,
        "not_license_for_redistribution":True
    }

def export_historical_csv(normalized,*,out_csv):
    if not isinstance(normalized,dict) or normalized.get("source")!="APPROVED_KITE_MCP_HISTORY":
        raise ValueError("Approved normalized Kite historical data required")
    target=Path(out_csv).expanduser()
    receipt=target.with_suffix(".receipt.json")
    if target.suffix.lower()!=".csv" or not target.parent.is_dir() or any(p.exists() or p.is_symlink() for p in (target,receipt)):
        raise ValueError("Choose a NEW CSV output in an existing approved directory")
    buff=io.StringIO(newline="")
    writer=csv.DictWriter(buff,fieldnames=["date","symbol","open","high","low","close","volume","source"])
    writer.writeheader()
    for r in normalized["rows"]:
        writer.writerow({"date":r["date"],"symbol":normalized["symbol"],"open":r["open"],
                         "high":r["high"],"low":r["low"],"close":r["close"],"volume":r["volume"],
                         "source":"APPROVED_KITE_MCP_HISTORY"})
    raw=buff.getvalue().encode("utf-8")
    metadata={k:v for k,v in normalized.items() if k!="rows"}
    metadata["csv_sha256"]=sha256(raw).hexdigest()
    created=[]
    try:
        with target.open("xb") as f:f.write(raw)
        created.append(target)
        with receipt.open("x",encoding="utf-8") as f:json.dump(metadata,f,indent=2,sort_keys=True)
        created.append(receipt)
    except Exception:
        for p in created:p.unlink(missing_ok=True)
        raise
    return {"csv_file":str(target),"receipt_file":str(receipt),
            "observations":len(normalized["rows"]),
            "csv_sha256":metadata["csv_sha256"],
            "trading_authority":False}
