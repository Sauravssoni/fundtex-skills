"""Fundtex Agent Desk: one research request -> source-aware analyst pack.

Live = authenticated, opt-in BROKER QUOTE SNAPSHOT only, not a continuous stream.
Public history = unofficial best-effort Yahoo chart data, never exchange certified.
Research cannot claim issuer fundamentals without original primary documents.
"""
from __future__ import annotations

import csv
from datetime import date,datetime,timezone
import io
import json
from pathlib import Path
import tempfile
import zipfile

from .broker_quotes import availability as broker_status, quote as broker_quote
from .market import validate_symbol, yahoo_prices
from .chart_studio import prices as audited_csv_prices
from .mission import mission
from .pack_studio import build_pack

def _history(symbol,*,source,csv_file=None,period="1y",public_fetch=None):
    sym=validate_symbol(symbol)
    if source=="csv":
        if not csv_file:raise ValueError("Approved --csv required for local historical data")
        raw=audited_csv_prices(csv_file,sym)
        raw["source"]="csv:"+Path(csv_file).name
        with open(csv_file,newline="",encoding="utf-8-sig") as handle:
            reader=csv.DictReader(handle)
            is_synthetic=any((r.get("source")=="SYNTHETIC_FIXTURE" or r.get("data_quality")=="SYNTHETIC_FIXTURE")
                             and (not r.get("symbol") or r.get("symbol","").strip().upper()==sym)
                             for r in reader)
        q="SYNTHETIC_FIXTURE" if is_synthetic else "USER_SUPPLIED_UNVERIFIED"
        return raw,raw["rows"],q,"Approved user CSV (FICTIONAL demo)" if is_synthetic else "Approved user CSV (authenticity unverified)"
    if source=="fyers":
        if csv_file:raise ValueError("--csv may only be supplied with --source csv")
        from .fyers_data import history as fyers_history
        result=(public_fetch or fyers_history)(sym,range_=period,interval="1d")
        return result,result["rows"],"AUTHENTICATED_FYERS_HISTORY_NOT_TICK_STREAM","FYERS official authenticated daily historical OHLCV"
    if source=="public":
        if csv_file:raise ValueError("--csv may only be supplied with --source csv")
        result=(public_fetch or yahoo_prices)(sym,range_=period,interval="1d")
        return result,result["rows"],"UNOFFICIAL_BEST_EFFORT_DELAYED","Yahoo Finance chart history (unofficial best effort; timestamp and adjustments unverified)"
    raise ValueError("Source must be public, fyers or csv; demo data is never a fallback")

def _quote_result(symbol,provider,*,quote_fetch=None):
    if provider=="off":
        return {"status":"NOT_REQUESTED","live_authenticated":False},None
    if provider=="auto":
        connected=broker_status()
        provider=next((x for x in ("fyers","kite","dhan") if connected.get(x)),None)
        if not provider:
            return {"status":"NO_CONFIGURED_BROKER","live_authenticated":False,
                    "action":"Connect authorized FYERS, Kite or Dhan account to enable current quote snapshots; no live price inferred"},None
    if provider not in ("fyers","kite","dhan"):raise ValueError("Invalid broker quote provider")
    # Auth failures are not converted to fabricated prices or fallback providers.
    result=(quote_fetch or broker_quote)(symbol,provider)
    if result["symbol"]!=symbol:raise ValueError("Broker returned different instrument")
    if result.get("provider")!=provider:raise ValueError("Broker provider mismatch")
    return {"status":"AUTHENTICATED_SNAPSHOT","live_authenticated":True,"provider":provider},result

def run(symbol,out,*,source="public",csv_file=None,period="1y",quote_provider="auto",
        max_age_days=7,fetch_public=None,fetch_quote=None,add_zip=True):
    sym=validate_symbol(symbol)
    if period not in ("1mo","3mo","6mo","1y","2y","5y"):raise ValueError("Unsupported historical range")
    if source=="fyers" and period in ("2y","5y"):raise ValueError("FYERS source supports up to 1y per request")
    if not isinstance(max_age_days,int) or not 0<=max_age_days<=365:
        raise ValueError("Max data age must be 0..365 days")
    folder=Path(out)
    if folder.exists() or (add_zip and folder.with_suffix(".zip").exists()):
        raise ValueError("Report folder or ZIP already exists; never overwrite past analyst reports")
    raw,rows,quality,provider=_history(sym,source=source,csv_file=csv_file,period=period,public_fetch=fetch_public)
    if len(rows)<12:raise ValueError("At least 12 real/approved observations required; no synthetic padding")
    observed=date.fromisoformat(rows[-1]["date"])
    age=(datetime.now(timezone.utc).date()-observed).days
    if age<0:raise ValueError("Historical feed contained future observation")
    if source in ("public","fyers") and age>max_age_days:
        raise ValueError("Historical provider observation stale by "+str(age)+" days; refusing to present as current data")
    # Snapshot retrieval must complete before creation; failure cannot silently downgrade the response.
    status,snapshot=_quote_result(sym,quote_provider,quote_fetch=fetch_quote)
    with tempfile.TemporaryDirectory(prefix="fundtex-agent-desk-") as work:
        stage=Path(work)/"source-history.csv"
        temp=io.StringIO(newline="")
        writer=csv.writer(temp)
        has_ohlc=all(all(k in row for k in ("open","high","low")) for row in rows)
        cols=["date","symbol"]+(["open","high","low"] if has_ohlc else [])+["close","volume","source"]
        writer.writerow(cols)
        for row in rows:
            writer.writerow([row["date"],sym]+([row["open"],row["high"],row["low"]] if has_ohlc else [])+[row["close"],row.get("volume"),quality])
        stage.write_text(temp.getvalue(),encoding="utf-8")
        result=build_pack(stage,sym,folder,data_quality=quality,provider=provider)
    # Safe append-only generated files, no credentials and no raw private client documents.
    source_record={
        "symbol":sym,"historical_provider":provider,"historical_data_quality":quality,
        "history_source_uri":raw.get("source","approved local CSV"),
        "source_snapshot_sha256":result["source_sha256"],
        "published_observation_date":observed.isoformat(),
        "age_days":age,"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
        "historical_data_is_streaming_live":False,
        "price_adjustment_review":"UNVERIFIED",
        "primary_issuer_fundamentals":"NOT_RETRIEVED_NOT_VERIFIED",
        "broker_quote_status":status,
        "research_only":True
    }
    (folder/"source-evidence.json").write_text(json.dumps(source_record,indent=2),encoding="utf-8")
    result["created_files"].append("source-evidence.json")
    if snapshot is not None:
        (folder/"authenticated-quote-snapshot.json").write_text(json.dumps(snapshot,indent=2),encoding="utf-8")
        result["created_files"].append("authenticated-quote-snapshot.json")
    prompt=mission(
        f"Indian listed company source evidence, fundamental diligence, comparative valuation and risk research for {sym}",
        agent="generic",mode="INSTITUTIONAL",abilities=("terminal","python"),max_workers=5,confirmed_permission=False)
    (folder/"agent-mission.json").write_text(json.dumps(prompt,indent=2),encoding="utf-8")
    result["created_files"].append("agent-mission.json")
    report=(
        "# FUNDTEX | AUTOMATED INDIA ANALYST DESK\n\n"
        f"**Security:** {sym}  \n**Historical data:** {provider}  \n"
        f"**Historical observation:** {observed.isoformat()} ({age} calendar days before retrieval)  \n"
        f"**Classification:** {quality}  \n**Authenticated quote:** {status['status']}\n\n"
        "## Completed automatically\n\n"
        "Historical price chart, descriptive moving averages/RSI, source-hashed CSV history, "
        "historical crossovers, return distribution and independent skeptic research-plan. "
        "Optional Excel/PDF/PNG outputs depend on available approved renderers; see manifest.\n\n"
        "## Missing evidence / human research required\n\n"
        "No original issuer financial statements, earnings audit notes, exchange announcements, "
        "corporate-action adjustments, market-data licensing rights, or predictive alpha are independently certified. "
        "An authorized coding agent should open dated original filings and conduct independent review before "
        "representing this as institutional investment research.\n\n"
        "## Interpretation\n\n"
        "A broker LTP is a *retrieved snapshot*, not a WebSocket streaming quote; it cannot be substituted "
        "for the historical chart series. A source last observed today does not prove a continuous real-time feed. "
        "If no broker was authorized or connected, the report contains no invented current quote.\n"
    )
    (folder/"START_HERE.md").write_text(report,encoding="utf-8")
    result["created_files"].append("START_HERE.md")
    result["version"]="1.0-agent-desk"
    result["historical_source_quality"]=quality
    result["broker_quote"]=status
    result["source_observation_age_days"]=age
    result["live_exchange_streaming"]=False
    result["quote_record_file"]="authenticated-quote-snapshot.json" if snapshot else None
    (folder/"manifest.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    if add_zip:
        zpath=folder.with_suffix(".zip")
        if zpath.exists():raise ValueError("Report ZIP path already exists")
        with zipfile.ZipFile(zpath,"x",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for path in sorted(folder.rglob("*")):
                if path.is_file():
                    if path.stat().st_size>15_000_000:raise ValueError("Individual report file exceeds 15 MB")
                    z.write(path,path.relative_to(folder).as_posix())
        result["zip"]=str(zpath)
    result["output_directory"]=str(folder)
    return result
