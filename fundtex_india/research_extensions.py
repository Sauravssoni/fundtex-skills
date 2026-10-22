"""Quantitative, headline and downside evidence pack with explicit research gates.

This is not independent primary-filing verification or actionable trading advice.
Each tool is optional but reports its failure/insufficient-data reasons.
"""
from __future__ import annotations
from collections import Counter
import datetime as dt
from email.utils import parsedate_to_datetime
import json
import math
from pathlib import Path

from .stats import report as historical_risk
from .forecast import prequential
from .godeye import walkforward
from .news import discover

TOPICS={
    "earnings_or_guidance":("earnings","guidance","profit","revenue","quarter","results","margin","ebitda"),
    "corporate_governance":("fraud","audit","governance","regulator","penalty","sebi","investigation","lawsuit"),
    "capital_structure":("debt","dilution","fundraise","buyback","dividend","pledge"),
    "downside_or_disruption":("decline","miss","downgrade","layoffs","cuts","loss","slump","risk","weak"),
    "upside_narrative":("upgrade","rally","gain","beats","growth","surge","optimism","rise"),
}
def _metadata_sentiment(news):
    """Only keyword *mentions*. Never pretend to parse articles or forecast prices."""
    output=[];counts=Counter()
    for x in news.get("items",[])[:12]:
        title=str(x.get("headline") or "").strip()
        words=set(__import__("re").findall(r"[a-z]+",title.lower()))
        labels=[topic for topic, terms in TOPICS.items() if any(term in words for term in terms)]
        for label in labels:counts[label]+=1
        try:
            timestamp=parsedate_to_datetime(x["published_raw"]).astimezone(dt.timezone.utc).isoformat()
        except (TypeError,ValueError,OverflowError,KeyError):
            timestamp=None
        output.append({"title":title[:350],"publisher":x.get("publisher"),
                       "publication_time_utc_unverified":timestamp,
                       "article_url":x.get("url"),"headline_topic_flags":labels,
                       "source_quality":"UNVERIFIED_HEADLINE_DISCOVERY"})
    return {"method":"TRANSPARENT_HEADLINE_KEYWORD_TOPIC_FLAGS_NOT_SENTIMENT_MODEL",
            "total_headlines":len(output),
            "topic_mentions":dict(counts),
            "articles_opened_and_verified":0,
            "sentiment_signal":"NOT_VALIDATED_UNSUITABLE_FOR_TRADING",
            "predictive_score":None,
            "events":output,
            "warnings":[
                "Headlines may concern other issuers; title match is not proof of relevance",
                "Keywords ignore negation and context; do not infer factual events from headlines",
                "Open primary filings and dated articles to verify any significant claim"
            ]}
def write_extra(folder,rows,symbol,*,include_news=True,news_fetch=None,window=120):
    folder=Path(folder)
    created=[]
    issues={}
    def save(name,body):
        target=folder/name
        with target.open("x",encoding="utf-8") as stream:
            json.dump(body,stream,indent=2,ensure_ascii=False,allow_nan=False)
        created.append(name)
    if len(rows)>=30:
        save("risk-diagnostics.json",{
            "classification":"HISTORICAL_DESCRIPTIVE_NOT_FORWARD_RISK_LIMIT",
            "numbers":historical_risk(rows),
            "issuer_fundamentals_verified":False})
    else:issues["risk-diagnostics.json"]="Need 30 dated price closes; none fabricated."
    if len(rows)>=window+100:
        try:
            forecast=prequential(rows,window=window)
            save("forecast-validation.json",forecast)
        except (ValueError,ArithmeticError) as exc:issues["forecast-validation.json"]=str(exc)
    else:issues["forecast-validation.json"]=f"Need at least {window+100} sessions for chronological scoring."
    if len(rows)>=150:
        try:
            check=walkforward(rows,min_train=120,lookback=60,cost_bps=12)
            save("walkforward-reality-check.json",check)
        except (ValueError,ArithmeticError) as exc:issues["walkforward-reality-check.json"]=str(exc)
    else:issues["walkforward-reality-check.json"]="Need at least 150 dated observations for this research test."
    if include_news:
        try:
            feed=(news_fetch or discover)(symbol.split(".")[0],limit=12)
            if not isinstance(feed,dict) or not isinstance(feed.get("items"),list):
                raise ValueError("Invalid news provider response")
            save("news-leads-unverified.json",feed)
            save("headline-topic-monitor.json",_metadata_sentiment(feed))
        except (ValueError,OSError,TimeoutError,KeyError,TypeError) as exc:
            issues["news-leads-unverified.json"]=f"News discovery unavailable: {type(exc).__name__}; no sentiment implied"
    else:
        issues["news-leads-unverified.json"]="News discovery disabled (no external keyword sent)."
    return {"created":created,"unavailable":issues,
            "source_reliance":"PRICE_HISTORY_ONLY_AND_UNVERIFIED_NEWS_LEADS",
            "not_a_profitable_or_licensed_live_predictive_model":True}
