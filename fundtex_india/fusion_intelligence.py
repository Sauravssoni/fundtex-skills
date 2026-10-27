"""FundTex Fusion Desk: attributable external intelligence, NOT a price oracle.

Original standalone implementation. World Monitor/Fincept AGPL source is NOT
included, fetched, repackaged or imported here. Source data must be provided
by an explicitly authorized host with provider metadata and terms respected.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

CATEGORIES={"geopolitics","macro","energy","shipping","trade","cyber",
            "natural_disaster","policy","market","company","other"}
MAX_EVENTS=300
MAX_BYTES=2_000_000
SOURCES={"WORLD_MONITOR_AUTHORIZED_MCP","NSE_PRIMARY","BSE_PRIMARY",
         "RBI_PRIMARY","SEBI_PRIMARY","REPUTABLE_NEWS_USER_APPROVED",
         "USER_SUPPLIED_UNVERIFIED"}
def _utc(value, field):
    if not isinstance(value,str) or len(value)>45:
        raise ValueError(field+" must be a bounded timezone-aware ISO timestamp")
    try: dt=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError:raise ValueError(field+" malformed ISO timestamp") from None
    if dt.tzinfo is None:raise ValueError(field+" requires explicit timezone")
    return dt.astimezone(timezone.utc)

def _event(item, now):
    if not isinstance(item,dict):
        raise ValueError("Every evidence event must be an object")
    allow={"source","source_url","headline","category","published_at","observed_at",
           "regions","symbols","summary","event_id"}
    if set(item)-allow:raise ValueError("Unsupported event fields: no opaque account or trade payloads")
    src=item.get("source")
    if src not in SOURCES:raise ValueError("Explicit allowlisted provider tag required")
    cat=item.get("category")
    if cat not in CATEGORIES:raise ValueError("Unknown event category")
    name=item.get("headline")
    if not isinstance(name,str) or not 8<=len(name.strip())<=280:
        raise ValueError("Dated evidence headline required")
    published=_utc(item.get("published_at"),"published_at")
    observed=_utc(item.get("observed_at"),"observed_at")
    if published>now or observed>now or published>observed:
        raise ValueError("Future or time-inconsistent publication prohibited")
    url=item.get("source_url")
    if url is not None:
        from urllib.parse import urlsplit
        try: u=urlsplit(url)
        except ValueError:raise ValueError("Malformed source URL") from None
        if u.scheme!="https" or not u.netloc or u.username or u.password or len(url)>700:
            raise ValueError("Only attributable HTTPS sources without embedded credentials")
    raw_regions=item.get("regions",[])
    raw_symbols=item.get("symbols",[])
    if not isinstance(raw_regions,list) or len(raw_regions)>10 or any(not isinstance(x,str) or len(x)>60 for x in raw_regions):
        raise ValueError("Invalid bounded region list")
    if not isinstance(raw_symbols,list) or len(raw_symbols)>25 or any(not isinstance(x,str) or len(x)>30 for x in raw_symbols):
        raise ValueError("Invalid bounded entity labels")
    note=item.get("summary","")
    if not isinstance(note,str) or len(note)>1000:raise ValueError("Summary size exceeded")
    external_id=item.get("event_id","")
    if not isinstance(external_id,str) or len(external_id)>160:raise ValueError("Invalid event_id")
    fingerprint=hashlib.sha256(json.dumps((src,external_id or name.strip().casefold(),published.isoformat()),
                                    separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
    age_hours=(now-published).total_seconds()/3600
    return {"id":fingerprint[:24],"source":src,"source_url":url,
      "category":cat,"headline":name.strip(),"published_at_utc":published.isoformat(),
      "observed_at_utc":observed.isoformat(),"age_hours":round(age_hours,2),
      "freshness":"CURRENT_LE_48H" if age_hours<=48 else "STALE_HISTORICAL",
      "regions":sorted(set(raw_regions)),"symbols":sorted(set(raw_symbols)),
      "summary":note.strip(),"source_claims_primary":src in {"NSE_PRIMARY","BSE_PRIMARY","RBI_PRIMARY","SEBI_PRIMARY"},
      "verified_primary":False, # An imported JSON source tag cannot authenticate the provider.
      "causality_verified":False,"trade_signal":False}

def from_file(path,*,as_of=None):
    f=Path(path).expanduser()
    if not f.is_file() or f.is_symlink() or f.stat().st_size>MAX_BYTES:
        raise ValueError("Approved existing evidence JSON must be <=2 MB and not symlink")
    now=_utc(as_of,"as_of") if as_of else datetime.now(timezone.utc)
    raw=f.read_bytes()
    try:items=json.loads(raw)
    except (ValueError,UnicodeError):raise ValueError("Evidence input must be a complete JSON list") from None
    if not isinstance(items,list) or len(items)>MAX_EVENTS:
        raise ValueError("Expected <=300 approved externally sourced events")
    out=[];seen=set();duplicates=0
    for item in items:
        e=_event(item,now)
        if e["id"] in seen:duplicates+=1;continue
        seen.add(e["id"]);out.append(e)
    out.sort(key=lambda e:(e["published_at_utc"],e["id"]),reverse=True)
    return {"product":"FundTex Fusion Intelligence","status":"USER_APPROVED_EVIDENCE_RESEARCH_ONLY",
      "provider_fetch_performed":False,"broker_access_performed":False,
      "exchange_live_price_verified":False,"news_prediction_verified":False,
      "no_trade_authority":True,"licence_to_redistribute":False,
      "source_sha256":hashlib.sha256(raw).hexdigest(),"as_of_utc":now.isoformat(),
      "source_verified_by_signed_provider":False,
      "event_count":len(out),"deduplicated":duplicates,
      "primary_events":0, # Only a trusted direct source connector can establish verified provenance.
      "claimed_primary_events":sum(e["source_claims_primary"] for e in out),
      "stale_events":sum(e["freshness"]=="STALE_HISTORICAL" for e in out),
      "events":out,
      "interpretation":"Independent evidence leads, never mathematical proof that an event will move a given market."}

def fuse(*,evidence,tradereplay=None,symbol=None):
    if not isinstance(evidence,dict) or evidence.get("status")!="USER_APPROVED_EVIDENCE_RESEARCH_ONLY":
        raise ValueError("Require verified structure from approved evidence input")
    if tradereplay is not None and (not isinstance(tradereplay,dict) or tradereplay.get("engine")!="FUNDTEX_INTRADAY_REPLAY_V1"):
        raise ValueError("Replay report must be from FundTex's bounded independent engine")
    if symbol is not None and (not isinstance(symbol,str) or len(symbol)>40):
        raise ValueError("Invalid review symbol")
    mentions=[e for e in evidence["events"] if symbol and symbol in e["symbols"]]
    caution=bool(evidence["stale_events"] or (evidence["event_count"]==0) or
                 (tradereplay and tradereplay["evaluation"]["sample_sessions"]<20))
    return {"engine":"FUNDTEX_GOD_EYE_FUSION_V1",
      "evidence_hash":evidence["source_sha256"],"as_of_utc":evidence["as_of_utc"],
      "provider_count":len({e["source"] for e in evidence["events"]}),
      "event_count":evidence["event_count"],"exact_symbol_mentions":len(mentions),
      "risk_context":{"macro_and_events":len([e for e in evidence["events"] if e["category"] in
             {"geopolitics","macro","energy","shipping","trade","cyber","policy"}]),
       "stale_or_missing":caution,
       "uncorroborated_market_causation":True},
      "replay":tradereplay,
      "terminal_panels":["India Market","Primary Filings","World Risk","Event Clock",
                         "Intraday Replay","Strategies","Kronos Bench","Risk Council",
                         "Evidence Ledger","Adversarial Review"],
      "agents_recommended":["primary_sources","world_risk","quant_risk","independent_skeptic"],
      "decision":"ABSTAIN_UNVERIFIED_EDGE",
      "broker_order_authority":False,
      "no_trade_actions":True,
      "notices":["World intelligence is contextual evidence, not a market-entry prediction.",
                 "A replay uses historical complete sessions, not order-book or exchange-verified fills.",
                 "Fincept/WorldMonitor third-party AGPL code is neither copied nor sublicensed."]}
