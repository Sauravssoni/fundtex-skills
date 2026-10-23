"""Opt-in read-only DhanHQ v2 options-chain snapshot adapter.

No orders, GTT, margin, funding, account discovery, trading, write APIs,
key persistence or silent network activity. Broker quote timestamps are NOT
present in Dhan's documented payload; local capture time is not quote age.
User supplies UnderlyingScrip/UnderlyingSeg/contract identity and lot size
from actual exchange instrument master; never guess mapping.
"""
from __future__ import annotations
import csv
from datetime import date, datetime, timezone
from hashlib import sha256
import io
import json
import math
import os
from pathlib import Path
import re
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

OFFICIAL_DOC="https://dhanhq.co/docs/v2/option-chain/"
URL="https://api.dhan.co/v2/optionchain"
SEGMENTS=frozenset(("IDX_I","NSE_EQ","BSE_EQ","IDX","BSE_FNO"))
SYMBOL_RE=re.compile(r"^[A-Z0-9][A-Z0-9_.-]{0,39}$")
FIELDS=("symbol","expiry","kind","strike","bid","ask","lot_size","as_of",
        "source","snapshot_id","quote_captured_utc","security_id",
        "bid_qty","ask_qty","volume","open_interest","spread_bps")
class _RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Dhan quote authorization must not follow redirects")

def _int(x,name,min_=1,max_=1_000_000):
    if isinstance(x,bool) or not isinstance(x,int) or not min_<=x<=max_:
        raise ValueError(f"Invalid {name}, expected integer {min_}..{max_}")
    return x

def _price(x,name,allow_zero=False):
    if isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x):
        raise ValueError(f"Invalid {name}: expected finite numeric field")
    if x<0 or (not allow_zero and x==0):
        raise ValueError(f"Invalid {name}: negative or nonpositive")
    return float(x)

def verify_config(config):
    if not isinstance(config,dict) or set(config)!={"underlying","underlying_scrip","underlying_seg","expiry","lot_size","max_strikes"}:
        raise ValueError("Provide exactly underlying, underlying_scrip, underlying_seg, expiry, lot_size, max_strikes")
    name=config["underlying"]
    if not isinstance(name,str) or not SYMBOL_RE.fullmatch(name):
        raise ValueError("Explicit short verified option underlying required")
    _int(config["underlying_scrip"],"underlying_scrip",1,2_147_483_647)
    segment=config["underlying_seg"]
    if not isinstance(segment,str) or segment not in SEGMENTS:
        raise ValueError("Exchange/segment needs explicit verified Dhan segment identifier")
    _int(config["lot_size"],"lot_size",1,100_000)
    _int(config["max_strikes"],"max_strikes",2,50)
    try:
        expiry=date.fromisoformat(config["expiry"])
    except (TypeError,ValueError):
        raise ValueError("expiry must be ISO YYYY-MM-DD") from None
    return expiry

def read_only_fetch(config, *, transport=None):
    """One owner-authorized read-only POST; no generic paths, fallback or redirects.

    Dhan documents an option-chain rate limit of one unique request per 3s.
    A caller must throttle subsequent requests and obey client entitlement.
    """
    verify_config(config)
    token=os.getenv("FUNDTEX_DHAN_ACCESS_TOKEN")
    client=os.getenv("FUNDTEX_DHAN_CLIENT_ID")
    if not token or not client:
        raise ValueError("Dhan authentication NOT_CONFIGURED; authorize privately in supported host")
    if len(token)>8192 or not client.isdigit() or len(client)>24:
        raise ValueError("Invalid Dhan credential format; never echo credentials")
    req=urllib.request.Request(
        URL,
        data=json.dumps({"UnderlyingScrip":config["underlying_scrip"],
                         "UnderlyingSeg":config["underlying_seg"],
                         "Expiry":config["expiry"]},separators=(",",":")).encode("ascii"),
        headers={"Content-Type":"application/json","access-token":token,
                 "client-id":client,"Accept":"application/json"},
        method="POST")
    if transport is None:
        opener=urllib.request.build_opener(_RejectRedirects())
        def transport(req):
            with opener.open(req,timeout=15) as res:
                if res.status!=200:raise ValueError("Dhan read-only market-data request unsuccessful")
                content=res.read(2_000_001)
            if len(content)>2_000_000:raise ValueError("Oversized Dhan option chain")
            return json.loads(content)
    try:
        payload=transport(req)
    except (urllib.error.URLError,TimeoutError,OSError) as exc:
        raise ValueError("Dhan read-only fetch failed; no data or quote inferred") from None
    return payload

def normalize(payload,config,*,captured_utc=None):
    """Strict normalization from ONE saved Dhan response; no network access."""
    expiry=verify_config(config)
    captured= captured_utc or datetime.now(timezone.utc)
    if not isinstance(captured,datetime) or captured.tzinfo is None:
        raise ValueError("Use timezone-aware UTC capture timestamp")
    captured=captured.astimezone(timezone.utc)
    if captured.date()>expiry:
        raise ValueError("Expired contracts: no current option chain claimed")
    if not isinstance(payload,dict) or payload.get("status")!="success":
        raise ValueError("Dhan source returned no successful option chain")
    body=payload.get("data")
    if not isinstance(body,dict):
        raise ValueError("Missing Dhan chain data")
    spot=_price(body.get("last_price"),"underlying reference price")
    chain=body.get("oc")
    if not isinstance(chain,dict) or not 2<=len(chain)<=2000:
        raise ValueError("Dhan option strike map missing or oversized")
    strikes=[]
    for k,v in chain.items():
        try: strike=float(k)
        except (ValueError,TypeError):raise ValueError("Invalid provider strike") from None
        if not math.isfinite(strike) or strike<=0 or not isinstance(v,dict):
            raise ValueError("Invalid quote strike/contract object")
        strikes.append((abs(strike-spot),strike,v))
    # Bounded selection from exactly one response, not multiple stale pulls.
    strikes.sort(key=lambda x:(x[0],x[1]))
    chosen=sorted(strikes[:config["max_strikes"]],key=lambda x:x[1])
    snapshot_sha=sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    fields=[]
    skipped=0
    seen=set()
    for _,strike,contracts in chosen:
        for k,kind in (("ce","call"),("pe","put")):
            entry=contracts.get(k)
            if entry is None:
                skipped+=1
                continue
            if not isinstance(entry,dict):
                raise ValueError("Malformed Dhan option contract")
            contract_id=_int(entry.get("security_id"),"security_id",1,2_147_483_647)
            key=(kind,strike)
            if key in seen:raise ValueError("Duplicate option contract strike")
            seen.add(key)
            bid=_price(entry.get("top_bid_price"),"bid price",True)
            ask=_price(entry.get("top_ask_price"),"ask price",True)
            bq=_int(entry.get("top_bid_quantity"),"bid quantity",0,10_000_000)
            aq=_int(entry.get("top_ask_quantity"),"ask quantity",0,10_000_000)
            volume=_int(entry.get("volume"),"volume",0,2_000_000_000)
            oi=_int(entry.get("oi"),"OI",0,2_000_000_000)
            # Absent bid, ask or top size is an untradeable snapshot leg,
            # not valid zero-slippage executable evidence.
            if bid<=0 or ask<=0 or bq<=0 or aq<=0:
                skipped+=1
                continue
            if ask<bid:
                raise ValueError("Crossed option quotes cannot be used for research")
            spread_bps=10_000*(ask-bid)/((ask+bid)/2)
            fields.append({
                "symbol":config["underlying"],"expiry":expiry.isoformat(),
                "kind":kind,"strike":strike,
                "bid":bid,"ask":ask,"lot_size":config["lot_size"],
                "as_of":captured.astimezone(ZoneInfo("Asia/Kolkata")).date().isoformat(),
                "source":"DHAN_AUTHENTICATED_FETCH_TIME_ONLY" if payload.get("_fundtex_capture_origin")=="authenticated" else "DHAN_USER_APPROVED_JSON_SNAPSHOT",
                "snapshot_id":snapshot_sha[:20],"quote_captured_utc":captured.isoformat(),
                "security_id":contract_id,"bid_qty":bq,"ask_qty":aq,
                "volume":volume,"open_interest":oi,"spread_bps":round(spread_bps,5)
            })
    if len(fields)<2:
        raise ValueError("Not enough valid option quotes with genuine bid/ask and displayed size")
    if len(fields)>100:
        raise ValueError("Too many option contracts for bounded downstream builder")
    dest=io.StringIO(newline="")
    w=csv.DictWriter(dest,fieldnames=FIELDS,lineterminator="\n")
    w.writeheader();w.writerows(fields)
    return {
        "csv":dest.getvalue(),
        "receipt":{"engine":"FUNDTEX_DHAN_SNAPSHOT_NORMALIZER_v1",
                   "underlying":config["underlying"],"broker_underlying_scrip":config["underlying_scrip"],
                   "broker_underlying_segment":config["underlying_seg"],
                   "expiry":expiry.isoformat(),"underlying_reference_ltp":spot,
                   "lot_size_user_verified":False,"user_supplied_lot_size":config["lot_size"],
                   "capture_utc":captured.isoformat(),"source_snapshot_sha256":snapshot_sha,
                   "quoted_contracts_accepted":len(fields),"omitted_contracts":skipped,
                   "contract_snapshot_exchange_timestamp":"NOT_PUBLISHED_IN_DOCUMENTED_PAYLOAD",
                   "provider_authentication_verified":payload.get("_fundtex_capture_origin")=="authenticated",
                   "broker_trade_margin_verified":False,"licensed_market_data_redistribution_allowed":False,
                   "expiry_and_lot_verified_against_nse_master":False,
                   "one_market_snapshot_not_trade_fills":True,"trading_authority":False,
                   "data_licensing":"Owner-authorized local research only; do not republish quote data",
                   "risk_note":"Dhan documents a 3-second option-chain rate limit; top bid/ask quantity is only displayed size, not simultaneous executable multi-leg liquidity.",
                   "documentation":OFFICIAL_DOC}
    }

def capture_to_files(config, *, out_csv, payload=None, captured_utc=None):
    """Create two new files atomically with no overwrite or token logging.

    Live only when caller explicitly invokes read_only_fetch and passes its data.
    """
    out=Path(out_csv).expanduser()
    if out.suffix.lower()!=".csv" or not out.parent.is_dir():
        raise ValueError("Choose a new CSV inside an existing approved directory")
    receipt_path=out.with_suffix(".receipt.json")
    if any(p.exists() or p.is_symlink() for p in (out,receipt_path)):
        raise ValueError("Existing quote snapshot file cannot be overwritten")
    if payload is None:
        raise ValueError("No option chain payload supplied; no fake fallback")
    normalized=normalize(payload,config,captured_utc=captured_utc)
    created=[]
    try:
        out.write_text(normalized["csv"],encoding="utf-8")
        created.append(out)
        normalized["receipt"]["csv_sha256"]=sha256(out.read_bytes()).hexdigest()
        receipt_path.write_text(json.dumps(normalized["receipt"],sort_keys=True,indent=2),encoding="utf-8")
        created.append(receipt_path)
    except Exception:
        for p in created:
            p.unlink(missing_ok=True)
        raise
    return {"csv_file":str(out),"receipt_file":str(receipt_path),**normalized["receipt"]}
