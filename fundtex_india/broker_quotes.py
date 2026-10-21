"""Read-only, permission-gated Indian brokerage quote snapshots.

Never sends orders, stores credentials, opens an exchange WebSocket, or claims
the historical candle chart is real-time. Brokers' data terms govern use.
"""
from __future__ import annotations
from datetime import datetime, timezone
import json
import math
import os
import re
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler
from .market import validate_symbol

MAX_RESPONSE=200_000

class BlockRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Broker API redirects are refused to protect authentication headers')

def _extract_ltp(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:
        raise ValueError("Broker returned invalid/absent latest traded price")
    return float(value)

def availability():
    return {
        "fyers":bool(os.getenv("FUNDTEX_FYERS_APP_ID") and os.getenv("FUNDTEX_FYERS_ACCESS_TOKEN")),
        "kite":bool(os.getenv("FUNDTEX_KITE_API_KEY") and os.getenv("FUNDTEX_KITE_ACCESS_TOKEN")),
        "dhan":bool(os.getenv("FUNDTEX_DHAN_CLIENT_ID") and os.getenv("FUNDTEX_DHAN_ACCESS_TOKEN")
                    and os.getenv("FUNDTEX_DHAN_SYMBOL_MAP")),
        "public_history":"best_effort_unofficial_delay_unknown",
        "demo":"synthetic_only",
        "licensed_exchange_feed_embedded":False
    }

def _request(url,headers,*,method="GET",body=None,timeout=7):
    if not (url.startswith("https://api.kite.trade/quote/ltp?") or url=="https://api.dhan.co/v2/marketfeed/ltp" or url.startswith("https://api-t1.fyers.in/data/quotes?") or url.startswith("https://api-t1.fyers.in/data/history?")):
        raise ValueError("Non-allowlisted broker endpoint")
    try:
        req=Request(url,headers=headers,data=body,method=method)
        with build_opener(BlockRedirects()).open(req,timeout=timeout) as res:
            if getattr(res,"status",0)!=200:
                raise ValueError("Unexpected broker quote status")
            raw=res.read(MAX_RESPONSE+1)
            if len(raw)>MAX_RESPONSE:raise ValueError("Broker response too large")
            return json.loads(raw)
    except (ValueError,KeyError):raise
    except Exception:
        raise ValueError("Broker quote unavailable; verify permissions and connection") from None

def parse_kite(payload,symbol):
    sym=validate_symbol(symbol)
    key=("NSE:" if sym.endswith(".NS") else "BSE:")+sym.rsplit(".",1)[0]
    if payload.get("status")!="success":
        raise ValueError("Kite returned an unsuccessful response")
    item=payload.get("data",{}).get(key)
    if not isinstance(item,dict):
        raise ValueError("Quote missing for requested Kite instrument")
    return _quote(_extract_ltp(item.get("last_price")),sym,"kite",item.get("last_trade_time"),
                  "Authenticated Kite Connect LTP snapshot, subject to broker entitlement and exchange terms")

def parse_dhan(payload,symbol,security_id):
    sym=validate_symbol(symbol)
    key="NSE_EQ" if sym.endswith(".NS") else "BSE_EQ"
    if payload.get('status') not in (None,'success'):
        raise ValueError('Dhan returned an unsuccessful response')
    group=payload.get("data",{}).get(key,{})
    item=group.get(str(security_id)) if isinstance(group,dict) else None
    if not isinstance(item,dict):raise ValueError("Quote missing for approved Dhan instrument")
    ltp=item.get("last_price",item.get("ltp"))
    return _quote(_extract_ltp(ltp),sym,"dhan",None,
                  "Authenticated DhanHQ LTP snapshot; instrument id manually mapped, terms apply")

def _quote(ltp,sym,provider,source_time,note):
    return {"symbol":sym,"last_price_inr":ltp,"provider":provider,
            "quality":"AUTHENTICATED_BROKER_SNAPSHOT_NOT_WEBSOCKET",
            "publisher_trade_timestamp":source_time or None,
            "retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
            "research_only":True,"source_warning":note,"not_historical_chart":True}

def quote(symbol,provider,credentials=None):
    sym=validate_symbol(symbol)
    if credentials is not None and not isinstance(credentials,dict):
        raise ValueError("Invalid in-memory credential configuration")
    if provider=="fyers":
        if credentials is not None:
            raise ValueError("FYERS uses approved local environment credentials, not inline overrides")
        from .fyers_data import quote as fyers_quote
        return fyers_quote(sym)
    if provider=="kite":
        key=credentials.get("api_key") if credentials is not None else os.getenv("FUNDTEX_KITE_API_KEY")
        token=credentials.get("access_token") if credentials is not None else os.getenv("FUNDTEX_KITE_ACCESS_TOKEN")
        if not key or not token:raise ValueError("Kite credentials not configured; no quote was retrieved")
        exch="NSE" if sym.endswith(".NS") else "BSE"
        inst=f"{exch}:{sym.rsplit('.',1)[0]}"
        payload=_request("https://api.kite.trade/quote/ltp?"+urlencode({"i":inst}),
                         {"Authorization":f"token {key}:{token}","X-Kite-Version":"3"})
        return parse_kite(payload,sym)
    if provider=="dhan":
        token=credentials.get("access_token") if credentials is not None else os.getenv("FUNDTEX_DHAN_ACCESS_TOKEN")
        client=credentials.get("client_id") if credentials is not None else os.getenv("FUNDTEX_DHAN_CLIENT_ID")
        if credentials is not None:
            ids=credentials.get("symbol_map",{})
        else:
            try:ids=json.loads(os.getenv("FUNDTEX_DHAN_SYMBOL_MAP","{}"))
            except json.JSONDecodeError:raise ValueError("Invalid Dhan instrument mapping JSON") from None
        if not (token and client and ids):raise ValueError("Dhan credentials or instrument mapping missing")
        security=ids.get(sym) if isinstance(ids,dict) else None
        if not (isinstance(security,(str,int)) and re.fullmatch(r"\d{1,12}",str(security))):
            raise ValueError("Dhan security id for symbol not configured")
        exchange="NSE_EQ" if sym.endswith(".NS") else "BSE_EQ"
        payload=_request("https://api.dhan.co/v2/marketfeed/ltp",
                         {"Accept":"application/json","Content-Type":"application/json",
                          "access-token":token,"client-id":client},
                         method="POST",body=json.dumps({exchange:[int(security)]}).encode())
        return parse_dhan(payload,sym,str(security))
    raise ValueError("Unknown approved broker provider")
