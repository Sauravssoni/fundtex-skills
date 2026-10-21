"""AMFI daily mutual fund NAV snapshot parser: local user-authorized file only.

Supports current eight-field (2026) and legacy six-field semicolon formats.
No NAV forecasting, fund recommendations or AMFI redistribution.
"""
from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import hashlib
from pathlib import Path

MAX_BYTES=6_000_000
def parse(raw, *, query="", max_results=15, as_of=None):
    if not isinstance(raw,(bytes,str)):
        raise ValueError("NAV input must be bytes/text")
    data=raw if isinstance(raw,bytes) else raw.encode("utf-8")
    if len(data)>MAX_BYTES:
        raise ValueError("NAV input exceeds six MB")
    if not isinstance(max_results,int) or not 1<=max_results<=50:
        raise ValueError("max_results must be 1..50")
    if len(query)>120:
        raise ValueError("query too long")
    today=date.fromisoformat(as_of) if as_of else date.today()
    rows=[]
    skipped=0
    total=0
    schema=None
    section=""
    amc=""
    for row in data.decode("utf-8-sig",errors="strict").splitlines():
        line=row.strip()
        if not line: continue
        if line.startswith("Scheme Code;"):
            columns=[s.strip() for s in line.split(";")]
            schema=len(columns)
            if schema not in (6,8):
                raise ValueError("Unsupported AMFI header schema; update parser after validating issuer layout")
            continue
        parts=line.split(";")
        if len(parts)==1:
            if line.startswith(("Open Ended Schemes","Close Ended Schemes","Interval Fund")):
                section=line[:150]
            else:
                amc=line[:150]
            continue
        if schema not in (6,8) or len(parts)!=schema:
            skipped+=1
            continue
        total+=1
        if schema==8:
            code,isin1,isin2,name,plan,option,nav_text,day_text=map(str.strip,parts)
        else:
            code,isin1,isin2,name,nav_text,day_text=map(str.strip,parts)
            plan=option=""
        if not code.isdecimal() or not name or nav_text in ("","-","N.A.","NA"):
            skipped+=1
            continue
        try:
            nav=Decimal(nav_text)
            stamp=datetime.strptime(day_text,"%d-%b-%Y").date()
        except (InvalidOperation,ValueError):
            skipped+=1
            continue
        if not nav.is_finite() or nav<=0 or nav>Decimal("1000000000"):
            skipped+=1
            continue
        elapsed=(today-stamp).days
        entry={"scheme_code":code,"scheme_name":name,"amc":amc,"category":section,
               "plan":plan or None,"option":option or None,"isin":isin1 if isin1!="-" else (isin2 if isin2!="-" else None),
               "nav_inr":float(nav),"nav_date":stamp.isoformat(),
               "age_days":elapsed,"status":"FUTURE_DATED_VERIFY" if elapsed<0 else ("STALE_VERIFY" if elapsed>7 else "AS_OF_DATE_ONLY")}
        if not query or query.casefold() in (" ".join([code,name,amc,plan,option])).casefold():
            rows.append(entry)
    if schema is None:
        raise ValueError("AMFI Scheme Code header missing")
    rows.sort(key=lambda x:(x["scheme_name"].casefold(),x["plan"] or "",x["scheme_code"]))
    return {"data_source":"USER_SUPPLIED_AMFI_FORMAT_UNVERIFIED_ORIGIN",
            "schema_columns":schema,"source_sha256":hashlib.sha256(data).hexdigest(),
            "as_of":today.isoformat(),"observed_scheme_rows":total,"skipped_rows":skipped,
            "matching_schemes":len(rows),"returned_schemes":rows[:max_results],
            "note":"NAV is dated end-of-day and not a tradeable real-time price; downloaded file identity, redistribution rights, stale schemes and corporate actions require independent verification.",
            "research_only":True}

def from_file(filename, *, query="", max_results=15, as_of=None):
    p=Path(filename)
    if not p.is_file() or p.stat().st_size>MAX_BYTES:
        raise ValueError("NAV file missing or too large")
    return parse(p.read_bytes(),query=query,max_results=max_results,as_of=as_of)
