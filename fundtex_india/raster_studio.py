"""Pixel-chart export using optional existing Pillow (not a browser screenshot)."""
from __future__ import annotations
from pathlib import Path
from .chart_studio import NAVY,PAPER,CYAN,GOLD,GREEN,RED,MUTED,TEXT

def render(spec, filename, width=1440, height=840):
    target=Path(filename)
    if target.exists():raise ValueError("Raster chart exists; no overwrite")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise ValueError("Pillow not available for automatic PNG fallback") from None
    if len(spec["rows"])<2:raise ValueError("Cannot chart fewer than two rows")
    chart=Image.new("RGB",(width,height),NAVY)
    draw=ImageDraw.Draw(chart)
    try:
        font=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",15)
        small=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",12)
        header=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",24)
    except (OSError,ValueError):
        font=ImageFont.load_default();small=font;header=font
    draw.rounded_rectangle((32,74,width-32,height-38),radius=15,fill=PAPER)
    draw.text((80,34),"FUNDTEX  /  FINANCIAL INTELLIGENCE",fill=TEXT,font=header)
    draw.text((80,96),spec["symbol"]+"   ·   "+spec["data_quality"]+"   ·   "+spec["last_observation"],
              fill=CYAN,font=font)
    rows=spec["rows"];n=len(rows);left=88;right=width-100;top=153;bottom=height-132
    lo=min(r.get("low",r["close"]) for r in rows);hi=max(r.get("high",r["close"]) for r in rows)
    for item in spec["annotations"]:
        if item["type"]=="zone":lo=min(lo,item["low"]);hi=max(hi,item["high"])
        else:lo=min(lo,item["price"]);hi=max(hi,item["price"])
    spread=max(.01,hi-lo);lo-=spread*.06;hi+=spread*.06
    def x(i):return left+(right-left)*i/(n-1)
    def y(v):return top+(hi-v)/(hi-lo)*(bottom-top)
    for i in range(6):
        value=lo+(hi-lo)*i/5;yy=y(value)
        draw.line((left,yy,right,yy),fill="#253955",width=1)
        draw.text((right+12,yy-5),f"{value:,.2f}",fill=MUTED,font=small)
        idx=round((n-1)*i/5);xx=x(idx)
        draw.text((max(4,xx-38),bottom+15),rows[idx]["date"],fill=MUTED,font=small)
    for item in spec["annotations"]:
        if item["type"]=="level":
            yy=y(item["price"]);draw.line((left,yy,right,yy),fill=GOLD,width=2)
            draw.text((left+10,yy-19),item["label"][:50],fill=GOLD,font=small)
        elif item["type"]=="zone":
            a=int(y(item["high"]));b=int(y(item["low"]))
            draw.rectangle((left,a,right,b),fill="#414139",outline=GOLD,width=1)
            draw.text((left+10,a+6),item["label"][:50],fill=GOLD,font=small)
    if spec["price_type"]=="OHLC_CANDLE":
        w=max(1,min(12,int((right-left)/n*.58)))
        for i,r in enumerate(rows):
            xx=x(i);colour=GREEN if r["close"]>=r["open"] else RED
            draw.line((xx,y(r["high"]),xx,y(r["low"])),fill=colour,width=2)
            draw.rectangle((xx-w/2,y(max(r["open"],r["close"])),xx+w/2,
                           max(y(max(r["open"],r["close"]))+1,y(min(r["open"],r["close"])))),fill=colour)
    else:
        draw.line([(x(i),y(r["close"])) for i,r in enumerate(rows)],fill=CYAN,width=3)
    for label,colour in (("sma20","#f7c772"),("sma50","#d39de8")):
        values=spec["indicators"][label]
        pts=[(x(i),y(v)) for i,v in enumerate(values) if v is not None]
        if len(pts)>1:draw.line(pts,fill=colour,width=2)
    for item in spec["annotations"]:
        if item["type"]=="callout":
            matching=next((i for i,r in enumerate(rows) if r["date"]==item["date"]),None)
            if matching is not None:
                xx=x(matching);yy=y(item["price"]);draw.ellipse((xx-5,yy-5,xx+5,yy+5),fill=GOLD)
                draw.text((xx+10,yy-20),item["label"][:40],fill=GOLD,font=small)
    draw.text((left,height-92),"PRICE  •  SMA20  •  SMA50",fill=CYAN,font=font)
    draw.text((left,height-68),"Historical research only · no live quote feed · source hash: "+spec["source_sha256"][:16],
              fill=MUTED,font=small)
    target.parent.mkdir(parents=True,exist_ok=True)
    chart.save(target,format="PNG",optimize=True)
    return str(target)
