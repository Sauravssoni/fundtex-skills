"""Dated, source-aware Indian company diligence from explicitly provided figures.

No market-data fetch, no automated filing authentication or investment recommendation.
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from urllib.parse import urlsplit

COMPANY_FIELDS=("revenue","net_income","operating_cash_flow","capital_expenditure","gross_debt","cash_equivalents","shareholders_equity","receivables","ebitda","ebit","interest_expense")
LENDER_FIELDS=("gross_npa_pct","net_npa_pct","nim_pct","credit_cost_pct","capital_adequacy_pct","cet1_pct","provision_coverage_pct")
ALL=set(COMPANY_FIELDS)|set(LENDER_FIELDS)

def decimal_value(obj,key):
    if key not in obj or obj[key] is None:
        return None
    if isinstance(obj[key],bool):
        raise ValueError("Boolean is not a financial figure: "+key)
    try:
        val=Decimal(str(obj[key]))
    except (InvalidOperation,TypeError):
        raise ValueError("Invalid financial figure: "+key) from None
    if not val.is_finite() or abs(val)>Decimal("1e18"):
        raise ValueError("Non-finite or excessive value: "+key)
    return val

def fraction(a,b):
    return round(float(a/b),8) if a is not None and b is not None and b!=0 else None

def parse_sources(items):
    if not isinstance(items,list) or len(items)>50:
        raise ValueError("sources must be a list of up to 50 entries")
    out=[]
    for item in items:
        if not isinstance(item,dict):
            raise ValueError("Bad source row")
        name=str(item.get("title","")).strip()
        date=str(item.get("published_at","")).strip()
        link=str(item.get("url","")).strip()
        if not name or not date:
            raise ValueError("Sources require title and publication date")
        if link and (urlsplit(link).scheme!="https" or not urlsplit(link).hostname):
            raise ValueError("Source link requires HTTPS URL")
        out.append({"title":name,"published_at":date,"url":link or None,
                    "independently_verified":False})
    return out

def analyze(data):
    if not isinstance(data,dict):
        raise ValueError("Expected a JSON document")
    entity=data.get("company",{})
    if not isinstance(entity,dict):
        raise ValueError("Company must be an object")
    name=str(entity.get("name","")).strip()
    ticker=str(entity.get("symbol","")).strip()
    sector=str(entity.get("sector","general")).lower()
    if not name or not ticker or len(name)>160 or len(ticker)>40:
        raise ValueError("Company name and ticker required")
    if data.get("currency")!="INR" or data.get("unit") not in ("crore","lakh","rupees"):
        raise ValueError("Requires currency INR and explicit unit crore/lakh/rupees")
    period=str(data.get("fiscal_period","")).strip()
    if not period or len(period)>50:
        raise ValueError("Fiscal period required")
    current=data.get("current",{})
    previous=data.get("previous",{})
    if not isinstance(current,dict) or not isinstance(previous,dict) or not current or len(current)>50 or len(previous)>50:
        raise ValueError("Current/previous data objects invalid")
    if any(field not in ALL for field in (*current,*previous)):
        raise ValueError("Unknown metric; explicit schema change required")
    cur={k:decimal_value(current,k) for k in ALL}
    prev={k:decimal_value(previous,k) for k in ALL}
    quality=data.get("data_quality","USER_SUPPLIED_UNVERIFIED")
    if quality not in ("USER_SUPPLIED_UNVERIFIED","SYNTHETIC_FIXTURE"):
        raise ValueError("Data quality is never independently certified by this parser")
    sources=parse_sources(data.get("sources",[]))
    category="bank_or_nbfc" if any(t in sector for t in ("bank","nbfc","lender","finance")) else "operating_company"
    m={}
    issues=[]
    missing=[]
    if category=="bank_or_nbfc":
        for k in LENDER_FIELDS:
            n=cur[k]
            if n is not None and not 0<=n<=100:
                raise ValueError("Bank metric outside 0..100: "+k)
            m[k]=float(n) if n is not None else None
            if n is None:
                missing.append(k)
        for k in ("gross_npa_pct","net_npa_pct","nim_pct","credit_cost_pct","cet1_pct"):
            m[k+"_change_pp"]=float(cur[k]-prev[k]) if cur[k] is not None and prev[k] is not None else None
        if cur["gross_npa_pct"] is not None and cur["net_npa_pct"] is not None and cur["net_npa_pct"]>cur["gross_npa_pct"]:
            issues.append("Net NPA exceeds gross NPA in supplied figures; verify definitions and period.")
        if cur["capital_adequacy_pct"] is not None and cur["cet1_pct"] is not None and cur["cet1_pct"]>cur["capital_adequacy_pct"]:
            issues.append("CET1 appears higher than total capital adequacy; reconcile filed capital ratios.")
    else:
        rev=cur["revenue"]
        ni=cur["net_income"]
        ocf=cur["operating_cash_flow"]
        prior_rev=prev["revenue"]
        m["revenue_growth_yoy"]=fraction(rev-prior_rev,prior_rev) if rev is not None and prior_rev is not None and prior_rev>0 else None
        m["net_profit_margin"]=fraction(ni,rev)
        m["ebitda_margin"]=fraction(cur["ebitda"],rev)
        m["cash_conversion_ocf_to_profit"]=fraction(ocf,ni)
        m["free_cash_flow"]=float(ocf-cur["capital_expenditure"]) if ocf is not None and cur["capital_expenditure"] is not None else None
        debt=cur["gross_debt"]-cur["cash_equivalents"] if cur["gross_debt"] is not None and cur["cash_equivalents"] is not None else None
        m["net_debt"]=float(debt) if debt is not None else None
        m["net_debt_to_ebitda"]=fraction(debt,cur["ebitda"])
        m["interest_coverage_ebit"]=fraction(cur["ebit"],cur["interest_expense"])
        m["receivables_to_revenue"]=fraction(cur["receivables"],rev)
        missing=[k for k in ("revenue","net_income","operating_cash_flow","capital_expenditure","ebitda") if cur[k] is None]
        if ni is not None and ni>0 and ocf is not None and ocf/ni<Decimal(".6"):
            issues.append("Reported positive profits convert poorly into operating cash: investigate receivables and one-offs.")
        if rev is not None and rev>0 and cur["receivables"] is not None and cur["receivables"]/rev>Decimal(".4"):
            issues.append("Receivables are substantial relative to annual revenue; check collections.")
        if debt is not None and cur["ebitda"] is not None and cur["ebitda"]>0 and debt/cur["ebitda"]>4:
            issues.append("Net debt exceeds four times EBITDA; assess maturities, covenants and liquidity.")
    if not sources:
        issues.insert(0,"No primary source register supplied; company figures unverified.")
    notes=[
        "Demo-only fictional figures; do NOT attribute to a real listed company." if quality=="SYNTHETIC_FIXTURE" else "User-supplied figures and URLs have NOT been independently opened or authenticated.",
        "Reconcile fiscal period, reporting scope, currency units, corporate actions, revisions and auditor disclosures.",
        "Sector-specific ratios are screening flags, not fraud findings or investment recommendations."
    ]
    return {
        "product":"Fundtex Financial Intelligence | Syntheon Technology",
        "type":"INDIA_FUNDAMENTAL_DILIGENCE",
        "company":{"name":name,"symbol":ticker,"sector":sector},
        "fiscal_period":period,"currency":"INR","unit":data["unit"],"classification":category,
        "data_quality":quality,
        "reported_metrics":{k:float(v) for k,v in cur.items() if v is not None},
        "derived_metrics":m,"forensic_questions":issues,"missing_fields":sorted(missing),
        "sources":sources,"limitations":notes,"research_only":True,"investment_recommendation":None
    }

def from_json(path):
    with Path(path).open(encoding="utf-8") as f:
        return analyze(json.load(f))

def render_markdown(packet):
    company=packet["company"]
    rows=[
        "# FUNDTEX / INDIA COMPANY DILIGENCE",
        "**"+company["name"]+"** ("+company["symbol"]+") — "+packet["fiscal_period"],
        "Data status: "+packet["data_quality"]+" | Units: INR "+packet["unit"],
        "",
        "## Financial checks",
        "| Measure | Value |",
        "|---|---:|"
    ]
    for k,v in sorted(packet["derived_metrics"].items()):
        rows.append("| "+k.replace("_"," ")+" | "+(str(v) if v is not None else "NOT PROVIDED")+" |")
    rows.extend(["","## Financial review questions"])
    rows.extend("- "+v for v in packet["forensic_questions"] or ["No calculation anomalies flagged; filing verification is still required."])
    rows.extend(["","## Missing essential data"])
    rows.extend("- "+v for v in packet["missing_fields"] or ["None for the limited validated fields."])
    rows.extend(["","## Source evidence"])
    rows.extend("- "+x["title"]+" ("+x["published_at"]+"): "+(x["url"] or "NO LINK")+" — NOT VERIFIED"
                for x in packet["sources"])
    if not packet["sources"]:
        rows.append("- NO SOURCE REGISTER")
    rows.extend(["","## Limitations"])
    rows.extend("- "+v for v in packet["limitations"])
    rows.extend(["","**Research assistance only. No automatic recommendation or price target.**"])
    return "\n".join(rows)+"\n"
