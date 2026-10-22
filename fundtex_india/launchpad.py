"""Optional offline Fundtex launchpad card for users who explicitly want a visual start.

No server, no JavaScript, no background polling, no secret/account inspection and no
implicit browser opening. Skills and research commands work without this screen.
"""
from __future__ import annotations
from datetime import datetime,timezone
from html import escape
from pathlib import Path
from urllib.parse import quote
import json
import os
import webbrowser

_STARTERS=(
    ("INSTITUTIONAL EQUITY DESK",
     "Analyze Infosys using dated filings, cash flow, source-checked charts, peers and a skeptical investment committee report."),
    ("HEDGED STRATEGY LAB",
     "Build and compare defined-risk NIFTY options payoff structures using approved actual quotes and verify risk, fees and settlement."),
    ("QUANT RESEARCH LAB",
     "Turn my SMA or RSI idea into an honest next-open backtest with held-out evaluation, realistic costs and negative cases."),
)
_OFFICIAL={
    "Kite official broker MCP":"https://zerodha.com/products/mcp/",
    "FYERS API documentation":"https://fyers.in/api-docs/v3/",
    "DhanHQ API documentation":"https://dhan.co/dhanhq/",
}

def render(*, installed_skills:bool, source_status:str, as_of_utc=None) -> str:
    source=escape(source_status[:80],quote=True)
    stamp=escape(as_of_utc or datetime.now(timezone.utc).isoformat())
    prompts="".join(
        '<section class="card"><small>'+escape(tag)+'</small><p>'+escape(prompt)+'</p></section>'
        for tag,prompt in _STARTERS
    )
    broker="".join('<a href="'+escape(url,quote=True)+'" rel="noopener noreferrer" target="_blank">'
                   +escape(name)+' ↗</a>' for name,url in _OFFICIAL.items())
    readiness="Ready to research in a permitted coding agent" if installed_skills else "Installed skills were not verified; run fundtex doctor"
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Fundtex | Start</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}
body{background:radial-gradient(circle at 85% 12%,#144773 0,transparent 35%),#050b15;color:#ebf4ff;font:16px/1.55 system-ui,-apple-system,Arial;margin:0;min-height:100vh}
main{max-width:1050px;margin:auto;padding:clamp(25px,6vw,74px)}
h1{font-size:clamp(32px,6vw,64px);letter-spacing:-.035em;line-height:1.1;margin:10px 0 17px}
h2{font-size:20px;margin:36px 0 14px}.tag{font-size:12px;letter-spacing:.16em;color:#a0d7fb;font-weight:700}
.lead{color:#b0cbe0;max-width:680px;font-size:18px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:13px;margin-top:26px}
.card{border:1px solid #274c6e;border-radius:18px;padding:20px;background:rgba(12,33,55,.72);min-height:166px}
.card p{font-size:15px;line-height:1.5}.card small{font-size:11px;letter-spacing:.09em;color:#80d6ff;font-weight:700}
.status{padding:11px 14px;border:1px solid #316481;border-radius:13px;background:rgba(17,49,74,.65);font-size:13px;color:#bde3f9}
.links{display:flex;flex-wrap:wrap;gap:12px}.links a{color:#acdbff;border:1px solid #3a6e91;padding:10px 14px;border-radius:12px;text-decoration:none}
footer{border-top:1px solid #24405a;margin-top:32px;padding-top:15px;color:#85a6bf;font-size:12px}
</style></head><body><main>
<div class="tag">SYNTHEON TECHNOLOGY  /  INDIA EDITION</div>
<h1>FUNDTEX <span style="color:#9dd9ff">INTELLIGENCE</span></h1>
<p class="lead">Your coding agent is the analyst. Ask naturally. Fundtex selects permitted sources, runs calculations, checks what is missing and produces research—not invented prices.</p>
<div class="status">"""+escape(readiness)+""" • Source: """+source+""" • As of """+stamp+"""</div>
<h2>What can your agent do?</h2><div class="cards">"""+prompts+"""</div>
<h2>Optional authorized broker connections</h2><p class="lead">Sign in directly with the broker. This page does not connect an account or collect a key.</p>
<div class="links">"""+broker+"""</div>
<footer>Research-only • No orders • No personal investment advice • Browser window is optional; your CLI skills do not depend on it.</footer>
</main></body></html>"""

def create(path:str, *, open_browser=False,installed_skills=False,source_status="NOT_AUTHENTICATED"):
    target=Path(path).expanduser()
    if not target.name.endswith(".html"):
        raise ValueError("Use a new .html output file")
    if target.is_symlink() or target.exists():
        raise ValueError("Never overwrite an existing or symlinked launchpad")
    if not target.parent.is_dir():
        raise ValueError("Choose an already existing approved output directory")
    if open_browser not in (True,False):
        raise ValueError("open_browser must be boolean")
    content=render(installed_skills=installed_skills,source_status=source_status)
    # No HTML embeds environment variables, file data, holdings, chats or credentials.
    with target.open("x",encoding="utf-8") as handle:
        handle.write(content)
    if open_browser:
        webbrowser.open(target.resolve().as_uri())
    return {"created":str(target),"browser_open_requested":bool(open_browser),
            "research_only":True,"no_credentials_processed":True,
            "underlying_market_data_connected":False}
