"""FundTex source-driven financial research film. No fabricated candles or advice.

A visually ambitious native renderer using optional Pillow and FFmpeg, with an
editable data/storyboard JSON and approved screenshot reference *hash only*.
huashu-motion is an OPTIONAL third-party finishing workflow, not secretly
installed or executed by this research engine.
"""
from __future__ import annotations
from datetime import datetime,timezone
from hashlib import sha256
import csv
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
from .chart_studio import prices, indicators

PALETTE={
    "bg":"#050B17","panel":"#0A1929","ink":"#EDF7FF",
    "muted":"#89AEC7","line":"#19394E","cyan":"#64E8FF",
    "blue":"#4C8EFF","green":"#42D8B4","red":"#FF718D","gold":"#FFD17E",
}
def _quality(csv_path, symbol):
    with Path(csv_path).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        observed=set()
        for r in reader:
            if not r.get("symbol") or r["symbol"].strip().upper()==symbol.upper():
                if r.get("source"):observed.add(r["source"].strip()[:90])
                if r.get("data_quality"):observed.add(r["data_quality"].strip()[:90])
    return "SYNTHETIC FIXTURE — NOT ACTUAL MARKET DATA" if "SYNTHETIC_FIXTURE" in observed else "UNVERIFIED INPUT — SOURCE: "+(", ".join(sorted(observed))[:100] or "USER CSV")

def storyboard(csv_path, symbol, *, reference_chart=None, seconds=10, fps=12):
    if isinstance(seconds,bool) or not isinstance(seconds,int) or not 6<=seconds<=30:
        raise ValueError("Duration must be integer 6..30 seconds")
    if isinstance(fps,bool) or not isinstance(fps,int) or not 6<=fps<=24:
        raise ValueError("Frame rate must be integer 6..24 fps")
    data=prices(csv_path,symbol)
    rows=data["rows"]
    if len(rows)>3000:raise ValueError("Film requires <=3000 history rows; select research period")
    inds=indicators(data)
    ref=None
    if reference_chart:
        path=Path(reference_chart).expanduser()
        if path.suffix.lower() not in (".png",".jpg",".jpeg",".webp") or not path.is_file() or path.stat().st_size>10_000_000:
            raise ValueError("Reference chart must be a local approved image <=10MB")
        # STYLE reference only, never OCR/extract prices or embed account data.
        ref={"sha256":sha256(path.read_bytes()).hexdigest(),"purpose":"VISUAL_STYLE_REFERENCE_ONLY_NOT_PRICE_SOURCE"}
    recent=rows[-min(len(rows),80):]
    first,last=recent[0]["close"],recent[-1]["close"]
    ret=100*(last/first-1)
    last_rsi=inds["rsi14"][-1]
    sma20=inds["sma20"][-1]
    sma50=inds["sma50"][-1]
    # Descriptive technical indicators only. Divergence not evidence of alpha.
    cross=inds["events"][-1] if inds["events"] else None
    narratives=[
        {"scene":"01 • MARKET CONTEXT","from":0,"to":.19,"text":"Price history, not a real-time trading signal"},
        {"scene":"02 • PRICE ACTION","from":.19,"to":.72,"text":"Observed bars progressively revealed in chronological order"},
        {"scene":"03 • INDICATOR REVIEW","from":.72,"to":.87,"text":"SMA20 / SMA50 and RSI14 are retrospective measurements"},
        {"scene":"04 • SKEPTICAL VERDICT","from":.87,"to":1.0,"text":"No calibrated forecast, trade execution or proven alpha"},
    ]
    return {
        "title":"FUNDTEX | FINANCIAL INTELLIGENCE FILM",
        "symbol":data["symbol"],"duration_seconds":seconds,"fps":fps,
        "frames":seconds*fps,"source_sha256":data["source_sha256"],
        "source_quality":_quality(csv_path,symbol),
        "observed_through":data["last_observation"],
        "window_start":recent[0]["date"],"window_end":recent[-1]["date"],
        "window_bars":len(recent),"ohlc_available":data["ohlc"],
        "start_close":round(first,4),"last_close":round(last,4),
        "historical_window_return_pct":round(ret,3),
        "rsi14_last":last_rsi,"sma20_last":sma20,"sma50_last":sma50,
        "last_historical_crossover":cross,
        "scenes":narratives,"reference_chart":ref,
        "narration_script":[
            f"{data['symbol']}: a source-labelled look through {data['last_observation']}.",
            f"In the last {len(recent)} sessions, the historical closing-price change was {ret:+.2f} percent.",
            f"The last RSI fourteen observation is {last_rsi if last_rsi is not None else 'unavailable'}. The moving averages describe history, not the next candle.",
            "Bull and bear scenarios remain uncertain. Brokerage, liquidity, corporate actions and market-data rights can materially change the analysis.",
            "This is retrospective research. No real-time quote, proven predictive signal or trading instruction is asserted."
        ],
        "trade_recommendation":"NONE","calibrated_prediction":False,
        "authenticated_broker_quote":False,"research_only":True
    },recent,inds

def _hex(c):
    return tuple(int(c[i:i+2],16) for i in (1,3,5))

def render_frame(canvas, story, rows, inds, i, *, font_file=None):
    from PIL import Image, ImageDraw, ImageFont
    W,H=canvas
    im=Image.new("RGB",(W,H),_hex(PALETTE["bg"]))
    d=ImageDraw.Draw(im)
    def text(x,y,t,size=19,color="ink",bold=False):
        if font_file:
            try:font=ImageFont.truetype(font_file,size)
            except OSError:font=ImageFont.load_default()
        else:
            path=("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf")
            try:font=ImageFont.truetype(path,size)
            except OSError:
                try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",size)
                except OSError:font=ImageFont.load_default()
        d.text((int(x),int(y)),str(t),fill=_hex(PALETTE.get(color,color)),font=font)
    progress=(i+1)/story["frames"]
    wmargin=int(W*.065)
    d.rounded_rectangle((wmargin,int(H*.19),W-wmargin,int(H*.76)),radius=18,fill=_hex(PALETTE["panel"]),outline=_hex(PALETTE["line"]),width=2)
    text(wmargin,int(H*.045),"FUNDTEX   /   INTELLIGENCE MOTION",20,"cyan",True)
    text(W-wmargin-240,int(H*.05),story["symbol"],19,"ink",True)
    stage=next((s for s in story["scenes"] if s["from"]<=progress<s["to"]),story["scenes"][-1])
    text(wmargin,int(H*.12),stage["scene"],16,"gold",True)
    n=len(rows);start=len(inds["sma20"])-n
    closing=[r["close"] for r in rows]
    lo=min((r.get("low",r["close"]) for r in rows))*.985
    hi=max((r.get("high",r["close"]) for r in rows))*1.015
    if hi<=lo:hi=lo+1
    xl=wmargin+38;xr=W-wmargin-25
    yt=H*.245;yb=H*.69
    def xx(k):return xl+k*(xr-xl)/max(1,n-1)
    def yy(v):return yb-(v-lo)/(hi-lo)*(yb-yt)
    for k in range(5):
        y=yt+(yb-yt)*k/4
        d.line((xl,y,xr,y),fill=_hex(PALETTE["line"]),width=1)
        text(xr-105,y+5,f"{hi-(hi-lo)*k/4:,.1f}",12,"muted")
    visible=max(2,min(n,int(n*max(0,(progress-.12)/.69))))
    if progress>.84:visible=n
    if story["ohlc_available"]:
        for k,r in enumerate(rows[:visible]):
            x=xx(k);up=r["close"]>=r["open"];col=_hex(PALETTE["green" if up else "red"])
            d.line((x,yy(r["low"]),x,yy(r["high"])),fill=col,width=2)
            bw=max(2,(xr-xl)/(n*2.2))
            d.rectangle((x-bw,yy(max(r["open"],r["close"])),x+bw,yy(min(r["open"],r["close"]))+1),fill=col)
    else:
        pts=[(xx(k),yy(v)) for k,v in enumerate(closing[:visible])]
        if len(pts)>1:d.line(pts,fill=_hex(PALETTE["cyan"]),width=3,joint="curve")
    def rolling(values,color):
        pts=[]
        for k in range(visible):
            v=values[start+k]
            if v is not None:pts.append((xx(k),yy(v)))
            elif len(pts)>1:d.line(pts,fill=_hex(PALETTE[color]),width=2);pts=[]
        if len(pts)>1:d.line(pts,fill=_hex(PALETTE[color]),width=2)
    if progress>.54:
        rolling(inds["sma20"],"gold")
        rolling(inds["sma50"],"blue")
    current=rows[visible-1]
    text(xl,int(H*.71),"AS OF "+current["date"],14,"muted")
    text(xr-210,int(H*.71),f"CLOSE  {current['close']:,.2f}",17,"ink",True)
    bottom=int(H*.81)
    text(wmargin,bottom,f"WINDOW {story['historical_window_return_pct']:+.2f}% (HISTORICAL)",18,"cyan",True)
    text(int(W*.61),bottom,f"RSI14  {story['rsi14_last'] if story['rsi14_last'] is not None else 'N/A'}",17,"gold")
    text(wmargin,int(H*.89),"NOT LIVE / NOT A TRADE SIGNAL • "+story["observed_through"],14,"red",True)
    quality=story["source_quality"][:100]
    text(wmargin,int(H*.94),quality+"  •  SHA256 "+story["source_sha256"][:12],11,"muted")
    # Native progress indicator, precise and deterministic across identical data.
    d.rectangle((0,H-5,int(W*progress),H),fill=_hex(PALETTE["cyan"]))
    return im

def create(csv_path,symbol,out_dir,*,reference_chart=None,seconds=10,fps=12,make_mp4=True):
    story,_,_=storyboard(csv_path,symbol,reference_chart=reference_chart,seconds=seconds,fps=fps)
    target=Path(out_dir).expanduser()
    if target.exists() or target.is_symlink() or not target.parent.is_dir():
        raise ValueError("Film output must be a NEW directory under an existing approved parent")
    if make_mp4 and (shutil.which("ffmpeg") is None):
        raise ValueError("FFmpeg unavailable; no fake MP4; use --storyboard-only")
    if make_mp4:
        try:import PIL
        except ImportError:raise ValueError("Pillow required to render native MP4; use --storyboard-only") from None
    # Validate and build before creating output to avoid leaving misleading partial files.
    data=prices(csv_path,symbol)
    inds=indicators(data);rows=data["rows"][-story["window_bars"]:]
    target.mkdir(mode=0o700)
    try:
        (target/"storyboard.json").write_text(json.dumps(story,indent=2),encoding="utf-8")
        (target/"narration.txt").write_text("\n\n".join(story["narration_script"]),encoding="utf-8")
        if make_mp4:
            with tempfile.TemporaryDirectory(prefix="fundtex-frames-") as scratch:
                frame_dir=Path(scratch)
                for i in range(story["frames"]):
                    render_frame((960,540),story,rows,inds,i).save(frame_dir/f"frame-{i:04d}.png")
                command=["ffmpeg","-hide_banner","-loglevel","error","-nostdin","-n",
                         "-framerate",str(fps),"-i",str(frame_dir/"frame-%04d.png"),
                         "-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p",
                         "-movflags","+faststart",str(target/"analysis.mp4")]
                run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180,check=False)
                if run.returncode!=0 or not (target/"analysis.mp4").is_file():
                    raise ValueError("FFmpeg render failed; no completed video claimed")
        return {"directory":str(target),
                "video":str(target/"analysis.mp4") if make_mp4 else None,
                "storyboard":str(target/"storyboard.json"),
                "narration":str(target/"narration.txt"),
                "frames":story["frames"],"source_sha256":story["source_sha256"],
                "source_quality":story["source_quality"],
                "reproducible_source_data":True,
                "video_audio":"NONE; voice/music requires separately authorized assets",
                "third_party_huashu":"NOT_INSTALLED_OR_CALLED",
                "trading_authority":False}
    except Exception:
        # Only remove files created in this new directory, never external user data.
        for p in target.iterdir():
            if p.is_file():p.unlink()
        target.rmdir()
        raise
