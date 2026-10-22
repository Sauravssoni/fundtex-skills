"""Fundtex Analyst Studio: deterministic audited price charts and chart signals.

No invented OHLC: close-only CSV -> line chart; candlesticks require actual
open/high/low/close. User-supplied files remain unverified until sourced.
"""
from __future__ import annotations
import csv
import datetime as dt
import hashlib
import html
import json
import math
from pathlib import Path

NAVY="#0b1120"; PAPER="#111c30"; GRID="#243149"; TEXT="#e9eef6"; MUTED="#9eb0cd"
CYAN="#6ae4db"; GREEN="#43d4aa"; RED="#f58497"; GOLD="#f7c772"
MAX_POINTS=20000

def prices(path, symbol):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>5_000_000:
        raise ValueError("Source CSV absent or exceeds 5MB")
    with p.open(newline="",encoding="utf-8-sig") as f:
        rdr=csv.DictReader(f)
        hdr=set(rdr.fieldnames or [])
        if "close" not in hdr or "date" not in hdr:
            raise ValueError("Expected date and close CSV columns")
        has_ohlc={"open","high","low","close"}<=hdr
        complete_ohlc_rows=False
        empty_ohlc_rows=False
        synthetic=False
        data=[]
        for row in rdr:
            if "symbol" in hdr and row.get("symbol","").strip().upper()!=symbol.upper():
                continue
            if row.get("data_quality")=="SYNTHETIC_FIXTURE" or row.get("source")=="SYNTHETIC_FIXTURE":synthetic=True
            date=dt.date.fromisoformat(str(row["date"]))
            if has_ohlc:
                blanks=[k for k in ("open","high","low") if row.get(k) in (None,"")]
                if len(blanks)==3:
                    empty_ohlc_rows=True
                elif blanks:
                    raise ValueError("Partial OHLC candle: open/high/low must all be present or all absent")
                else:
                    complete_ohlc_rows=True
                if empty_ohlc_rows and complete_ohlc_rows:
                    raise ValueError("Cannot mix close-only and full OHLC rows")
            fields=("open","high","low","close") if has_ohlc and complete_ohlc_rows else ("close",)
            values={k:float(row[k]) for k in fields}
            if any(not math.isfinite(v) or v<=0 for v in values.values()):
                raise ValueError("Nonfinite/nonpositive price")
            if has_ohlc:
                if values["low"]>min(values["open"],values["close"]) or values["high"]<max(values["open"],values["close"]) or values["high"]<values["low"]:
                    raise ValueError("OHLC constraints violated")
            vol=row.get("volume")
            if vol not in (None,""):
                vol=float(vol)
                if not math.isfinite(vol) or vol<0: raise ValueError("Invalid volume")
            else:vol=None
            data.append({"date":date.isoformat(),**values,"volume":vol})
            if len(data)>MAX_POINTS: raise ValueError("Too many price rows; filter first")
    if len(data)<12:raise ValueError("At least 12 observations needed for chart")
    dates=[x["date"] for x in data]
    if dates!=sorted(set(dates)):raise ValueError("Dates must be strictly increasing without duplicates")
    if dates[-1]>dt.datetime.now(dt.timezone.utc).date().isoformat():
        raise ValueError("Future date in price history")
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    return {"rows":data,"ohlc":has_ohlc and complete_ohlc_rows,"source_sha256":digest,"symbol":symbol.upper(),
            "data_quality":"SYNTHETIC_FIXTURE" if synthetic else "USER_SUPPLIED_UNVERIFIED","source_label":p.name,
            "last_observation":dates[-1]}

def sma(values,n):
    out=[None]*len(values);s=0.
    for i,v in enumerate(values):
        s+=v
        if i>=n:s-=values[i-n]
        if i>=n-1:out[i]=round(s/n,6)
    return out

def ema(values,n):
    out=[];prior=None;k=2/(n+1)
    for v in values:
        prior=v if prior is None else (v*k+prior*(1-k))
        out.append(round(prior,6))
    return out

def rsi(values,n=14):
    out=[None]*len(values)
    if len(values)<=n:return out
    gains=[max(0,values[i]-values[i-1]) for i in range(1,n+1)]
    losses=[max(0,values[i-1]-values[i]) for i in range(1,n+1)]
    avg_up=sum(gains)/n;avg_down=sum(losses)/n
    for i in range(n,len(values)):
        if i>n:
            diff=values[i]-values[i-1]
            avg_up=(avg_up*(n-1)+max(diff,0))/n
            avg_down=(avg_down*(n-1)+max(-diff,0))/n
        out[i]=(50.0 if avg_up==0 else 100.0) if avg_down==0 else round(100-100/(1+avg_up/avg_down),3)
    return out

def indicators(data):
    close=[r["close"] for r in data["rows"]]
    quick=sma(close,20);slow=sma(close,50)
    crossing=[]
    for i in range(1,len(close)):
        if quick[i] is None or slow[i] is None or quick[i-1] is None or slow[i-1] is None:continue
        # Retrospective descriptive crossovers, not validated future trading signals.
        prev=quick[i-1]-slow[i-1];cur=quick[i]-slow[i]
        if prev<=0<cur:crossing.append({"date":data["rows"][i]["date"],"price":close[i],"signal":"UPWARD_CROSS_HISTORICAL","not_investment_signal":True})
        if prev>=0>cur:crossing.append({"date":data["rows"][i]["date"],"price":close[i],"signal":"DOWNWARD_CROSS_HISTORICAL","not_investment_signal":True})
    return {"sma20":quick,"sma50":slow,"ema12":ema(close,12),"ema26":ema(close,26),"rsi14":rsi(close),"events":crossing}

def annotations_from_file(path):
    if not path:return []
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data,list) or len(data)>40:raise ValueError("Annotations require array <=40")
    output=[]
    for item in data:
        if not isinstance(item,dict) or item.get("type") not in ("level","zone","callout"):
            raise ValueError("Only level, zone and callout annotations supported")
        kind=item["type"];label=str(item.get("label",""))[:100]
        if "<" in label or ">" in label:label=label.replace("<","").replace(">","")
        a={"type":kind,"label":label}
        for key in (("price",) if kind=="level" else (("low","high") if kind=="zone" else ("price",))):
            val=float(item[key])
            if not math.isfinite(val) or val<=0:raise ValueError("Invalid annotation price")
            a[key]=val
        if kind=="zone" and a["low"]>=a["high"]:raise ValueError("Zone boundaries inverted")
        if kind=="callout":a["date"]=dt.date.fromisoformat(str(item["date"])).isoformat()
        output.append(a)
    return output

def chart_spec(data,notes=None):
    inds=indicators(data);rows=data["rows"]
    return {"title":data["symbol"]+" | Fundtex Analyst Studio",
            "symbol":data["symbol"],"price_type":"OHLC_CANDLE" if data["ohlc"] else "CLOSE_LINE",
            "rows":rows,"indicators":inds,"annotations":notes or [],"source_sha256":data["source_sha256"],
            "data_quality":data["data_quality"],"last_observation":data["last_observation"],
            "footer":"RESEARCH PREVIEW - source unverified; historical signals not recommendations",
            "no_live_feed":True}

def svg(spec,width=1440,height=840):
    if width<700 or width>3000 or height<460 or height>2000:raise ValueError("Invalid chart dimensions")
    rows=spec["rows"];n=len(rows);padx=86;right=width-95;top=118;bottom=height-152;w=right-padx;h=bottom-top
    low=min((x.get("low",x["close"]) for x in rows));high=max((x.get("high",x["close"]) for x in rows))
    for a in spec["annotations"]:
        if a["type"]=="zone":low=min(low,a["low"]);high=max(high,a["high"])
        else:low=min(low,a["price"]);high=max(high,a["price"])
    spread=max(1e-9,high-low);low-=spread*.07;high+=spread*.07
    def px(i):return padx+i/(n-1)*w
    def py(v):return top+(high-v)/(high-low)*h
    def esc(v):return html.escape(str(v),quote=True)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
           f'<rect width="{width}" height="{height}" fill="{NAVY}"/>',
           f'<rect x="34" y="72" width="{width-68}" height="{height-108}" rx="16" fill="{PAPER}"/>',
           f'<text x="76" y="53" fill="{TEXT}" font-family="Arial, sans-serif" font-size="29" font-weight="bold">FUNDTEX  /  ANALYST STUDIO</text>',
           f'<text x="{right}" y="52" text-anchor="end" fill="{CYAN}" font-size="16" font-family="Arial,sans-serif">{esc(spec["symbol"])}  •  {esc(spec["last_observation"])}</text>',
           f'<text x="{padx}" y="100" fill="{MUTED}" font-family="Arial,sans-serif" font-size="13">{esc(spec["data_quality"])}  ·  {esc(spec["price_type"])}</text>']
    for i in range(6):
        v=low+(high-low)*i/5;y=py(v)
        parts.append(f'<line x1="{padx}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{right+12}" y="{y+4:.1f}" fill="{MUTED}" font-family="Arial" font-size="12">{v:,.2f}</text>')
    for i in range(6):
        idx=round((n-1)*i/5);x=px(idx)
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="{GRID}" opacity=".35"/>')
        parts.append(f'<text x="{x:.1f}" y="{bottom+30}" text-anchor="middle" fill="{MUTED}" font-size="12" font-family="Arial">{rows[idx]["date"]}</text>')
    for a in spec["annotations"]:
        if a["type"]=="zone":
            ya=py(a["high"]);yb=py(a["low"])
            parts.append(f'<rect x="{padx}" y="{ya:.1f}" width="{w}" height="{yb-ya:.1f}" fill="{GOLD}" opacity=".13" stroke="{GOLD}" stroke-opacity=".4" stroke-dasharray="5 4"/>')
            parts.append(f'<text x="{padx+8}" y="{ya+17:.1f}" font-family="Arial" fill="{GOLD}" font-size="13">{esc(a["label"])}</text>')
        elif a["type"]=="level":
            y=py(a["price"])
            parts.append(f'<line x1="{padx}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{GOLD}" stroke-width="1.5" stroke-dasharray="7 5"/>')
            parts.append(f'<text x="{padx+8}" y="{y-7:.1f}" fill="{GOLD}" font-family="Arial" font-size="13">{esc(a["label"])}</text>')
    if spec["price_type"]=="OHLC_CANDLE":
        barw=max(1.2,min(12,w/n*.58))
        for i,r in enumerate(rows):
            x=px(i);colour=GREEN if r["close"]>=r["open"] else RED
            parts.append(f'<line x1="{x:.2f}" y1="{py(r["high"]):.2f}" x2="{x:.2f}" y2="{py(r["low"]):.2f}" stroke="{colour}" stroke-width="1.3"/>')
            y0=py(max(r["open"],r["close"]));yh=abs(py(r["open"])-py(r["close"]))
            parts.append(f'<rect x="{x-barw/2:.2f}" y="{y0:.2f}" width="{barw:.2f}" height="{max(1.2,yh):.2f}" fill="{colour}"/>')
    else:
        pts=" ".join(f"{px(i):.1f},{py(r['close']):.1f}" for i,r in enumerate(rows))
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{CYAN}" stroke-width="2.4"/>')
    for key,color in (("sma20","#f5c879"),("sma50","#d89bec")):
        vals=spec["indicators"][key];points=" ".join(f"{px(i):.1f},{py(v):.1f}" for i,v in enumerate(vals) if v is not None)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="1.8" opacity=".87"/>')
    for a in spec["annotations"]:
        if a["type"]=="callout":
            indices=[i for i,r in enumerate(rows) if r["date"]==a["date"]]
            if indices:
                x=px(indices[0]);y=py(a["price"])
                parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{GOLD}" stroke="{NAVY}" stroke-width="2"/>')
                parts.append(f'<text x="{x+12:.1f}" y="{y-12:.1f}" font-size="13" font-family="Arial" fill="{GOLD}">{esc(a["label"])}</text>')
    y=height-88
    parts.extend([f'<text x="85" y="{y}" font-family="Arial" font-size="14" fill="{CYAN}">● PRICE  </text>',
                  f'<text x="205" y="{y}" font-family="Arial" font-size="14" fill="#f5c879">━ SMA 20  </text>',
                  f'<text x="328" y="{y}" font-family="Arial" font-size="14" fill="#d89bec">━ SMA 50</text>',
                  f'<text x="85" y="{height-55}" font-family="Arial" font-size="12" fill="{MUTED}">{esc(spec["footer"])}</text>',
                  f'<text x="{right}" y="{height-55}" text-anchor="end" font-family="Arial" font-size="12" fill="{MUTED}">SHA256 {esc(spec["source_sha256"][:16])}…</text>','</svg>'])
    return "\n".join(parts)

def write_new(path,content):
    p=Path(path)
    if p.exists():raise ValueError("Output exists: "+str(p))
    p.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(content,bytes):p.write_bytes(content)
    else:p.write_text(content,encoding="utf-8")
    return str(p)
