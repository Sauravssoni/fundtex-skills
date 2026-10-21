"""One-page finance research memo from approved price-chart specification."""
from __future__ import annotations
import math
from pathlib import Path
from statistics import stdev

def memo(spec):
    closes=[r["close"] for r in spec["rows"]]
    ret=[b/a-1 for a,b in zip(closes,closes[1:])]
    vol=stdev(ret)*math.sqrt(252)*100 if len(ret)>2 else None
    moving=spec["indicators"]
    def show(x): return "NOT AVAILABLE" if x is None else f"{x:,.2f}"
    return (
        "# FUNDTEX | INDIA ANALYST RESEARCH MEMO\n\n"
        f"**Instrument:** {spec['symbol']}  \n"
        f"**Last observed:** {spec['last_observation']} (NOT LIVE)  \n"
        f"**Source quality:** {spec['data_quality']}  \n"
        f"**SHA256:** {spec['source_sha256']}\n\n"
        "## Executive observation\n\n"
        f"The approved sample contains {len(closes)} sessions. The closing price moved from "
        f"INR {closes[0]:,.2f} to INR {closes[-1]:,.2f} "
        f"({100*(closes[-1]/closes[0]-1):+.2f}%) within the sample. "
        f"Annualized historical daily-return volatility is {show(vol)}% (252-session approximation). "
        "None of these descriptive statistics forecasts a future outcome.\n\n"
        "## Historical technical indicators\n\n"
        "| Measure | Observed value |\n|---|---:|\n"
        f"| Last close (INR) | {show(closes[-1])} |\n"
        f"| SMA 20 (INR) | {show(moving['sma20'][-1])} |\n"
        f"| SMA 50 (INR) | {show(moving['sma50'][-1])} |\n"
        f"| RSI 14 | {show(moving['rsi14'][-1])} |\n"
        f"| Historical crossover count | {len(moving['events'])} |\n\n"
        "## Falsification: bull / bear / unknown\n\n"
        "**Bull hypothesis:** Historical price strength persists; requires independent fundamental and liquidity validation.\n\n"
        "**Bear hypothesis:** Apparent trend is transient, or vendor corporate-action adjustments change the chart.\n\n"
        "**Unknown:** No licensed live feed, issuer filings, current price validation or forward predictive edge established here.\n\n"
        "## Reviewer checklist\n\n"
        "1. Verify exact data publisher, authenticity, symbol, sample cutoff and split/dividend adjustments.\n"
        "2. Independently open and cite NSE/BSE/issuer fundamentals relevant to the question.\n"
        "3. Separate manually drawn visual levels from benchmarked investment signals.\n"
        "4. Obtain human investment-research and data-rights approval before external use.\n\n"
        "**Research preview only. No autonomous trading or personalized investment recommendation.**\n"
    )

def pdf(spec,path):
    target=Path(path)
    if target.exists():raise ValueError("PDF exists; refusing overwrite")
    try:
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
        from reportlab.lib.colors import HexColor
        from xml.sax.saxutils import escape
    except ImportError:
        raise ValueError("Optional reportlab missing; PDF skipped, Markdown memo remains available") from None
    txt=memo(spec);target.parent.mkdir(parents=True,exist_ok=True)
    styles=getSampleStyleSheet()
    h=ParagraphStyle("FTHead",parent=styles["Heading1"],fontSize=16,textColor=HexColor("#075773"),spaceAfter=12)
    sh=ParagraphStyle("FTSub",parent=styles["Heading2"],fontSize=11,textColor=HexColor("#133C57"),spaceBefore=12)
    b=ParagraphStyle("FTBody",parent=styles["BodyText"],fontSize=9,leading=13,spaceAfter=5)
    story=[];table=[]
    def flush():
        if not table:return
        cells=[[Paragraph(escape(item),b) for item in row] for row in table]
        t=Table(cells,colWidths=[190,210],repeatRows=1,hAlign="LEFT")
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),HexColor("#CBD9E4")),("ROWBACKGROUNDS",(0,1),(-1,-1),[HexColor("#EDF3F8"),HexColor("#FFFFFF")])]))
        story.append(t);table.clear()
    for line in txt.splitlines():
        if line.startswith("|"):
            cols=[x.strip() for x in line.strip("|").split("|")]
            if not all(set(x)<=set("-: ") for x in cols):table.append(cols)
            continue
        flush()
        if not line:story.append(Spacer(1,5));continue
        if line.startswith("# "):story.append(Paragraph(escape(line[2:]),h))
        elif line.startswith("## "):story.append(Paragraph(escape(line[3:]),sh))
        else:story.append(Paragraph(escape(line).replace("**",""),b))
    flush()
    doc=SimpleDocTemplate(str(target),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=52,bottomMargin=54)
    def deco(c,d):
        w,H=A4;c.setFillColor(HexColor("#0B2843"));c.rect(0,H-17,w,17,stroke=0,fill=1)
        c.setFont("Helvetica",7.5);c.setFillColor(HexColor("#6C7D8F"))
        c.drawString(42,28,"FUNDTEX  /  RESEARCH PREVIEW  /  VERIFY ALL PRIMARY SOURCES")
        c.drawRightString(w-42,28,f"Page {d.page}")
    doc.build(story,onFirstPage=deco,onLaterPages=deco)
    return str(target)
