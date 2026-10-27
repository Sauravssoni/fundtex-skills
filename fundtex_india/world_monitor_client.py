"""Direct read-only official World Monitor MCP adapter.

User explicitly approves data-bearing calls; HTTP endpoint is fixed and no
third-party app source is copied. Broker/auth data never enters the server.
"""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import urllib.request
import urllib.error

URL="https://worldmonitor.app/mcp"
TOOLS={"get_sources","get_world_brief","get_country_risk","get_market_data",
       "get_news_intelligence","get_chokepoint_status"}
FIELDS={
 "get_sources":{"view","kind","country","tier","risk","platform","query","limit"},
 "get_world_brief":{"geo_context"},
 "get_country_risk":{"country_code","history_days"},
 "get_market_data":{"symbols","asset_class","limit"},
 "get_news_intelligence":{"topic","category","country","alerts_only","query","min_importance","limit"},
 "get_chokepoint_status":{"chokepoint","dataset","limit"}
}
class _RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ValueError("Unexpected World Monitor endpoint redirect")
def _args(tool,args):
    if tool not in TOOLS:raise ValueError("Only six approved read-only World Monitor MCP tools")
    if not isinstance(args,dict) or set(args)-FIELDS[tool]:
        raise ValueError("Unsupported World Monitor arguments")
    def small(v):
        return isinstance(v,str) and 1<=len(v)<=120 and all(ord(c)>=32 for c in v)
    for k,v in args.items():
        if k in {"limit","history_days"}:
            if isinstance(v,bool) or not isinstance(v,int) or not 1<=v<=90:
                raise ValueError("Unsafe result/window bound")
        elif k=="symbols":
            if not isinstance(v,list) or not 1<=len(v)<=15 or any(not small(x) for x in v):
                raise ValueError("Expected <=15 explicit asset symbols")
        elif k=="alerts_only":
            if not isinstance(v,bool):raise ValueError("Boolean required")
        elif k=="min_importance":
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not 0<=v<=100:
                raise ValueError("Bounded numeric importance required")
        elif not small(v):raise ValueError("Non-empty bounded source query fields required")
    if tool=="get_country_risk" and (not isinstance(args.get("country_code"),str) or
         len(args["country_code"])!=2 or not args["country_code"].isupper()):
        raise ValueError("Explicit two-letter country_code required")
    return args

def read_only(tool="get_sources",*,args=None,out=None,approved=False,key_env="WORLD_MONITOR_API_KEY",opener=None):
    args=_args(tool,args or {})
    if tool!="get_sources" and approved is not True:
        raise ValueError("Explicit user-approved World Monitor data request required")
    if tool not in TOOLS:raise ValueError("Unsupported tool")
    token=os.environ.get(key_env,"")
    if tool!="get_sources" and not token:
        raise ValueError("World Monitor data-bearing tools need provider OAuth in host or a user-owned local API key environment variable")
    if token and (not token.startswith("wm_") or len(token)>128 or any(c.isspace() for c in token)):
        raise ValueError("Invalid provider key format; no network request attempted")
    if out is None:raise ValueError("Explicit NEW private JSON output path required")
    dest=Path(out).expanduser()
    if dest.suffix.lower()!=".json" or not dest.parent.is_dir() or dest.exists() or dest.is_symlink():
        raise ValueError("Choose a NEW private JSON output in an existing approved directory")
    request_body=json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call",
        "params":{"name":tool,"arguments":args}},separators=(",",":")).encode()
    headers={"content-type":"application/json","accept":"application/json",
             "mcp-protocol-version":"2025-03-26","user-agent":"FundTex-Research-Only/1"}
    if token and tool!="get_sources":headers["X-WorldMonitor-Key"]=token
    request=urllib.request.Request(URL,data=request_body,headers=headers,method="POST")
    handler=opener or urllib.request.build_opener(_RejectRedirect)
    try:
        with handler.open(request,timeout=12) as response:
            content_type=response.headers.get("Content-Type","")
            raw=response.read(2_000_001)
            if response.status!=200 or len(raw)>2_000_000 or "json" not in content_type:
                raise ValueError("Provider unavailable or oversized response; no report stored")
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as exc:
        raise ValueError("World Monitor connection/entitlement check failed; no data returned") from None
    try:payload=json.loads(raw)
    except (ValueError,UnicodeError):raise ValueError("Malformed provider JSON response") from None
    if not isinstance(payload,dict) or "error" in payload or not isinstance(payload.get("result"),dict):
        raise ValueError("Provider reported no authorized result")
    result=payload["result"]
    if result.get("isError") is True or not isinstance(result.get("content"),list):
        raise ValueError("World Monitor requested tool unavailable/unauthorized")
    # Keep the raw attributed response only in a user-approved private file;
    # never pass to another provider or claim source authentication by filename.
    with dest.open("xb") as handle:handle.write(raw)
    return {"provider":"WORLD_MONITOR_OFFICIAL_MCP","tool":tool,
      "requested_at_utc":datetime.now(timezone.utc).isoformat(),
      "stored_file":str(dest),"source_sha256":sha256(raw).hexdigest(),
      "provider_endpoint":URL,"provider_credentials_logged":False,
      "is_broker_market_quote":False,"licensed_redistribution_granted":False,
      "tool_result_available":True,"request_used_account_key":tool!="get_sources",
      "application_code_copied":False,"trading_enabled":False}
