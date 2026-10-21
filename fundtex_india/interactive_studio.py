"""Self-contained browser research chart, safe local-source refresh and optional screenshots."""
from __future__ import annotations
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .chart_studio import chart_spec, prices, svg, write_new

def document(spec, *, refresh=False):
    graphic=svg(spec)
    close=spec["rows"][-1]["close"]
    last_rsi=next((v for v in reversed(spec["indicators"]["rsi14"]) if v is not None),None)
    mode="LOCAL CSV RELOAD / NOT A LIVE EXCHANGE FEED" if refresh else "OFFLINE / USER-SUPPLIED CSV"
    return ("""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>FUNDTEX Analyst Studio</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{font-family:Inter,system-ui,-apple-system,sans-serif;background:#080e19;color:#e9eef6;margin:0}
.header{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:18px 26px;border-bottom:1px solid #273754}
.brand{font-weight:800;letter-spacing:.11em;font-size:18px}.brand em{font-style:normal;color:#6ae4db}.status{font-size:12px;color:#9eb0cd}
.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:12px;padding:16px 26px}button{border:1px solid #395774;background:#162842;border-radius:9px;color:#e9eef6;padding:11px 17px;font-size:13px;cursor:pointer;font-weight:650}
button:hover{border-color:#6ae4db}button.on{background:#0c4d52;color:#c5fff8;border-color:#6ae4db}
.metric{border:1px solid #273754;border-radius:9px;background:#101d30;padding:7px 12px;font-size:12px;min-width:105px}.metric b{display:block;color:white;font-size:17px}
.main{padding:0 26px}.chart{width:100%;border:1px solid #1e2d46;border-radius:12px;overflow:hidden}.chart svg{width:100%;height:auto;display:block}
.foot{font-size:12px;color:#8fa3c1;display:flex;gap:25px;flex-wrap:wrap;margin:14px 26px}
#notice{font-size:12px;color:#f7c772}svg line.userLevel{stroke:#6ae4db;stroke-dasharray:8 5;stroke-width:2}
</style></head><body><div class="header"><div class="brand">FUNDTEX <em>/ ANALYST STUDIO</em></div><div class="status">"""
    + html.escape(mode)+"""</div></div>
<div class="toolbar">
<div class="metric">LAST CLOSE <b>"""+format(close,",.2f")+"""</b></div>
<div class="metric">RSI 14 <b>"""+("—" if last_rsi is None else format(last_rsi,".1f"))+"""</b></div>
<button id="level">Draw level</button><button id="clear">Clear drawings</button>
<button id="refresh">Refresh local CSV</button><button id="png">Export PNG screenshot</button><button id="svg">Export SVG</button><button id="json">Export drawings JSON</button>
<span id="notice">Source unverified. No investment advice.</span>
</div><div class="main"><div class="chart" id="chart">"""+graphic+"""</div></div>
<div class="foot"><span>Horizontal levels are visual annotations only, not predictive trading signals.</span><span>Browser-native PNG and SVG exports work offline.</span><span>Refresh requires optional localhost viewer mode.</span></div>
<script>
'use strict';
const chart=document.getElementById('chart'),notice=document.getElementById('notice');
const levels=[];let levelMode=false;const W=1440,H=840;
function down(content,filename,mime){let a=document.createElement('a'),url=URL.createObjectURL(new Blob([content],{type:mime}));a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),2000)}
function currentSVG(){return chart.querySelector('svg')}
document.getElementById('level').onclick=function(){levelMode=!levelMode;this.classList.toggle('on',levelMode);notice.textContent=levelMode?'Click anywhere in the plot to mark a visual level':'Drawing paused'};
chart.onclick=function(ev){if(!levelMode)return;let g=currentSVG(),p=g.createSVGPoint();p.x=ev.clientX;p.y=ev.clientY;let pos=p.matrixTransform(g.getScreenCTM().inverse());if(pos.y<118||pos.y>H-152||pos.x<86||pos.x>W-95)return;let line=document.createElementNS('http://www.w3.org/2000/svg','line');line.setAttribute('x1','86');line.setAttribute('x2',String(W-95));line.setAttribute('y1',String(pos.y));line.setAttribute('y2',String(pos.y));line.setAttribute('class','userLevel');g.appendChild(line);levels.push({type:'visual_level',normalized_y:+(pos.y/H).toFixed(5),signal_status:'UNVERIFIED_MANUAL_DRAWING'});notice.textContent='Level drawn, export chart or notes'};
document.getElementById('clear').onclick=function(){currentSVG().querySelectorAll('.userLevel').forEach(x=>x.remove());levels.length=0;notice.textContent='Drawings cleared'};
document.getElementById('svg').onclick=()=>down(new XMLSerializer().serializeToString(currentSVG()),'fundtex-annotated-chart.svg','image/svg+xml');
document.getElementById('json').onclick=()=>down(JSON.stringify({source:'MANUAL_BROWSER_DRAWING',levels},null,2),'fundtex-drawings.json','application/json');
document.getElementById('png').onclick=function(){let xml=new XMLSerializer().serializeToString(currentSVG()),img=new Image(),url=URL.createObjectURL(new Blob([xml],{type:'image/svg+xml'}));img.onload=function(){const canvas=document.createElement('canvas');canvas.width=W;canvas.height=H;canvas.getContext('2d').drawImage(img,0,0,W,H);canvas.toBlob(blob=>{if(blob){let a=document.createElement('a'),u=URL.createObjectURL(blob);a.href=u;a.download='fundtex-annotated-chart.png';a.click();setTimeout(()=>URL.revokeObjectURL(u),2000)}});URL.revokeObjectURL(url)};img.onerror=()=>notice.textContent='PNG render blocked by browser - export SVG';img.src=url};
document.getElementById('refresh').onclick=async function(){try{const r=await fetch('/chart.svg',{cache:'no-store'});if(!r.ok)throw Error('not in local viewer mode');const xml=await r.text(),parser=new DOMParser(),doc=parser.parseFromString(xml,'image/svg+xml');if(!doc.documentElement||doc.querySelector('parsererror'))throw Error('malformed chart');chart.replaceChildren(document.importNode(doc.documentElement,true));levels.length=0;notice.textContent='Local source reloaded. Manual drawings cleared.'}catch(e){notice.textContent='Offline file: start the localhost viewer to refresh approved CSV.'}};
</script></body></html>""")

def local_serve(csv_path,symbol,notes=None,*,port=8734,once=False):
    """Only loopback; never serves requested paths or arbitrary filenames."""
    if port<1024 or port>65535:raise ValueError("Viewer port must be 1024..65535")
    source=Path(csv_path).resolve(strict=True)
    def load():
        return chart_spec(prices(source,symbol),notes)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            route=self.path.split("?")[0]
            if route not in ("/","/chart.svg","/healthz"):
                self.send_error(404);return
            try:
                spec=load()
                if route=="/":
                    body=document(spec,refresh=True).encode("utf-8");typ="text/html; charset=utf-8"
                elif route=="/chart.svg":
                    body=svg(spec).encode("utf-8");typ="image/svg+xml"
                else:
                    body=json.dumps({"ok":True,"symbol":symbol,"source_hash":spec["source_sha256"],"live_exchange_feed":False}).encode();typ="application/json"
                self.send_response(200);self.send_header("Content-Type",typ)
                self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff")
                self.send_header("Content-Security-Policy","default-src 'self' blob: data: 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'")
                self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
            except (ValueError,OSError):
                self.send_error(422,"Approved CSV not readable or invalid")
        def log_message(self,fmt,*args):
            return
    server=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    server.timeout=.2
    try:
        if once:server.handle_request()
        else:server.serve_forever(poll_interval=.25)
    finally:server.server_close()

def screenshot(html_path,out_path):
    """Optional installed Playwright/Chromium. Fail closed; use browser Export PNG fallback."""
    if Path(out_path).exists():raise ValueError("Will not overwrite existing screenshot")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ValueError("Playwright not installed; use chart page Export PNG or approved Playwright installation") from None
    infile=Path(html_path).resolve(strict=True)
    if infile.suffix.lower()!=".html":raise ValueError("Screenshot source must be local HTML")
    with sync_playwright() as playwright:
        try:
            browser=playwright.chromium.launch(headless=True)
        except Exception:
            raise ValueError("Chromium unavailable: run playwright install chromium or use browser Export PNG") from None
        try:
            page=browser.new_page(viewport={"width":1440,"height":1000},device_scale_factor=1)
            page.goto(infile.as_uri(),wait_until="load",timeout=15000)
            page.locator(".chart").screenshot(path=str(out_path))
        finally:
            browser.close()
    return str(out_path)
