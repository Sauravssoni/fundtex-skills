"""Approved-official RSS discovery and local evidence imports for Indian research.

No exchange scraping, proxying, automatic crawling, broker integrations or paid feeds.
Feed headlines are discovery metadata, not verified claims about economic events.
"""
from __future__ import annotations
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
import re
import urllib.error
import urllib.request
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

OFFICIAL_FEEDS = {
    "sebi": {"url":"https://www.sebi.gov.in/sebirss.xml",
             "source":"Securities and Exchange Board of India",
             "home":"https://www.sebi.gov.in/rss.html"},
    "rbi-releases": {"url":"https://rbi.org.in/pressreleases_rss.xml",
             "source":"Reserve Bank of India (press releases)",
             "home":"https://www.rbi.org.in/Scripts/rss.aspx"},
    "rbi-notifications": {"url":"https://rbi.org.in/notifications_rss.xml",
             "source":"Reserve Bank of India (notifications)",
             "home":"https://www.rbi.org.in/Scripts/rss.aspx"}
}
OTHER_SOURCES = {
    "issuer_filings":{"home":"https://www.sebi.gov.in/curation/corporate_filings.html",
                      "mode":"official_directory_manual_retrieval",
                      "restriction":"NSE/BSE usage and redistribution rights need review; no automated exchange scraper"},
    "amfi_nav":{"home":"https://www.amfiindia.com/net-asset-value",
                "mode":"user_supplied_download_parse",
                "restriction":"Snapshot and historical NAV must be correctly dated, provider usage rights verified"},
    "india_ogd":{"home":"https://data.gov.in/",
                "mode":"registered_api_or_user_supplied_dataset",
                "restriction":"Use licensed published resources; API key may be required; provenance/last update mandatory"},
    "rbi_dbie":{"home":"https://cimsdbie.rbi.org.in/",
                "mode":"official_dataset_export_manually",
                "restriction":"Verify release revisions and original RBI publication date; no unofficial mirrors"}
}
MAX_BYTES=1_000_000

class StrictRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        original=urlsplit(req.full_url)
        target=urlsplit(newurl)
        if target.scheme!="https" or original.hostname!=target.hostname:
            raise ValueError("Cross-host/non-HTTPS redirect blocked")
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def catalog():
    return {"product":"Fundtex India Verified-Source Discovery",
            "official_rss_feeds":OFFICIAL_FEEDS,"additional_source_adapters":OTHER_SOURCES,
            "live_market_data_entitlement":False,"research_only":True,
            "source_note":"Official feed URLs are publisher-supported. RSS metadata still needs full-document verification."}

def _timestamp(text):
    if not text:
        return None
    try:
        d=parsedate_to_datetime(text)
        if d.tzinfo is None:
            return None
        return d.astimezone(timezone.utc).isoformat()
    except (ValueError,TypeError,OverflowError):
        try:
            d=datetime.fromisoformat(text.replace("Z","+00:00"))
            return d.astimezone(timezone.utc).isoformat() if d.tzinfo else None
        except ValueError:
            return None

def parse_feed(xml, source, *, max_items=20):
    if not isinstance(xml,(str,bytes)):
        raise ValueError("RSS must be UTF-8 text or bytes")
    if not isinstance(max_items,int) or not 1<=max_items<=100:
        raise ValueError("max_items must be 1..100")
    data=xml.encode("utf-8") if isinstance(xml,str) else xml
    if len(data)>MAX_BYTES:
        raise ValueError("RSS file exceeds 1 MB safety cap")
    if re.search(br"<!DOCTYPE|<!ENTITY",data,re.IGNORECASE):
        raise ValueError("DTD/entity declarations are not permitted")
    try:
        root=ET.fromstring(data)
    except ET.ParseError:
        raise ValueError("Feed is not valid XML") from None
    if root.tag not in ("rss","{http://www.w3.org/2005/Atom}feed"):
        raise ValueError("Expected RSS2 or Atom feed")
    atom=root.tag!="rss"
    entries=(root.findall("{http://www.w3.org/2005/Atom}entry") if atom else root.findall("./channel/item"))
    out=[]
    for item in entries[:max_items]:
        def get(tag):
            node=item.find(tag)
            return ((node.text or "").strip() if node is not None else "")
        if atom:
            ns="{http://www.w3.org/2005/Atom}"
            title=get(ns+"title")
            node=item.find(ns+"link")
            link=(node.attrib.get("href","").strip() if node is not None else "")
            date=get(ns+"updated") or get(ns+"published")
        else:
            title=get("title")
            link=get("link")
            date=get("pubDate") or get("{http://purl.org/dc/elements/1.1/}date")
        u=urlsplit(link)
        if not title or len(title)>400 or u.scheme!="https" or not u.hostname:
            # Invalid entries are skipped; do not substitute a fabricated official URL.
            continue
        out.append({"title":title,"url":link,"published_at_utc":_timestamp(date),
                    "raw_published_date":date or None,
                    "source_feed":source,"source_status":"OFFICIAL_FEED_METADATA_UNVERIFIED_CONTENT",
                    "requires_opening_link":True})
    return {"feed":source,"source_status":"UNVERIFIED_FEED_ITEMS",
            "input_sha256":hashlib.sha256(data).hexdigest(),"items_returned":len(out),
            "items":out,"note":"Headlines and dates come from the feed; claims must be verified by opening the original document."}

def from_file(path, *, source="user-provided-rss", max_items=20):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>MAX_BYTES:
        raise ValueError("Feed file missing or exceeds size limit")
    return parse_feed(p.read_bytes(),source,max_items=max_items)

def fetch(name, *, max_items=20, timeout=8):
    if name not in OFFICIAL_FEEDS:
        raise ValueError("Only explicitly approved official RSS feeds are supported")
    if not isinstance(timeout,(int,float)) or not 1<=timeout<=20:
        raise ValueError("Network timeout must be 1..20 seconds")
    target=OFFICIAL_FEEDS[name]["url"]
    opener=urllib.request.build_opener(StrictRedirectHandler())
    req=urllib.request.Request(target,headers={"User-Agent":"Fundtex-Research-ReadOnly/0.8 (contact: repository owner; no redistribution)","Accept":"application/rss+xml, application/xml, text/xml"})
    try:
        with opener.open(req,timeout=timeout) as resp:
            if resp.status!=200:
                raise ValueError("Unexpected official feed response status")
            typ=resp.headers.get_content_type()
            if typ not in ("application/xml","text/xml","application/rss+xml","application/atom+xml","text/plain"):
                raise ValueError("Non-feed content type returned: "+typ)
            body=resp.read(MAX_BYTES+1)
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError) as exc:
        raise ValueError("Official feed unavailable; use an authorized saved XML copy: "+type(exc).__name__) from None
    result=parse_feed(body,name,max_items=max_items)
    result["official_feed_url"]=target
    result["fetched_at_utc"]=datetime.now(timezone.utc).isoformat()
    result["source_access"]="LIVE_OFFICIAL_RSS_METADATA_ONLY"
    return result
