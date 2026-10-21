"""India market news DISCOVERY from Google News RSS; headlines require source verification."""
from __future__ import annotations
import datetime as dt
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

def discover(query: str, limit: int = 10):
    query = query.strip()
    if not query or len(query) > 120 or not 1 <= limit <= 50:
        raise ValueError("Need a query <=120 characters and limit between 1 and 50")
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": f"{query} (NSE OR BSE OR India stock market)",
        "hl": "en-IN", "gl": "IN", "ceid": "IN:en"
    })
    req = urllib.request.Request(url, headers={"User-Agent":"FundtexResearch/0.1 (market news discovery)"})
    with urllib.request.urlopen(req, timeout=12) as response:
        root = ET.fromstring(response.read(2_000_000))
    items = []
    for item in root.findall("./channel/item")[:limit]:
        source_node = item.find("source")
        items.append({
            "headline": (item.findtext("title") or "").strip(),
            "url": (item.findtext("link") or "").strip(),
            "published_raw": item.findtext("pubDate"),
            "publisher": source_node.text if source_node is not None else None,
            "quality": "UNVERIFIED_HEADLINE_DISCOVERY",
            "note": "Open linked story and verify primary company/exchange filing before use."
        })
    return {"query":query, "feed":url, "retrieved_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "items":items, "quality":"DISCOVERY_ONLY_NOT_EXCHANGE_FILINGS"}
