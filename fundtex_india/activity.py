"""Optional localhost-only Fundtex agent-activity companion.

Shows real, opt-in host-emitted events; does not scrape a model's hidden reasoning.
No external telemetry, command execution, accounts, quotes or broker credentials.
"""
from __future__ import annotations
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import html
import json
import os
import re
import webbrowser

_VALID_NAME = re.compile(r"^[a-zA-Z0-9 _.:-]{1,60}$")
_ALLOWED = ("start", "progress", "done", "error", "blocked")
_SECRET = re.compile(r"(?i)(access[_ -]?token|api[_ -]?key|password|authorization:|bearer |secret|otp|cookie:)")
_LIMIT = 2_000_000

def _file(path):
    target = Path(path).expanduser().absolute()
    if not target.parent.is_dir():
        raise ValueError("Event directory must already exist and be approved")
    if target.is_symlink():
        raise ValueError("Refusing symlink event log")
    return target

def emit(path, *, agent, event, status, detail=""):
    """Append a bounded JSONL event. Identifiers must be emitted by the real agent host."""
    target = _file(path)
    if not all(isinstance(x, str) for x in (agent, event, status, detail)):
        raise ValueError("Expected string event fields")
    if not _VALID_NAME.fullmatch(agent) or not _VALID_NAME.fullmatch(event):
        raise ValueError("Agent/event must be short printable identifiers")
    if status not in _ALLOWED:
        raise ValueError("Invalid lifecycle status")
    if len(detail) > 160 or "\n" in detail or "\r" in detail or _SECRET.search(detail):
        raise ValueError("Do not log prompts, secrets, credentials or long/private payloads")
    if target.exists() and target.stat().st_size >= _LIMIT:
        raise ValueError("Event file reached 2 MB; rotate it manually")
    record = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "agent": agent, "event": event, "status": status, "detail": detail}
    payload = (json.dumps(record, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"): flags |= os.O_NOFOLLOW
    descriptor = os.open(target, flags, 0o600)
    try:
        os.write(descriptor, payload)
    finally:
        os.close(descriptor)
    return {"recorded": True, "event": event, "status": status, "data_sent_off_device": False}

def read_events(path, *, limit=100):
    target = _file(path)
    if not target.exists(): return []
    if target.stat().st_size > _LIMIT:
        raise ValueError("Event log too large; refuse to expose contents")
    if not isinstance(limit, int) or not 1 <= limit <= 200:
        raise ValueError("limit out of range")
    entries = []
    for line in target.read_text(encoding="utf-8").splitlines()[-limit:]:
        try: event = json.loads(line)
        except json.JSONDecodeError: continue
        if isinstance(event, dict) and all(isinstance(event.get(k), str) for k in ("agent", "event", "status", "timestamp_utc")):
            entries.append({k: str(event.get(k, ""))[:160] for k in ("timestamp_utc", "agent", "event", "status", "detail")})
    return entries

_PAGE = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fundtex | Agent Activity</title>
<style>body{font:15px system-ui;background:#0b1120;color:#e5ecf5;max-width:1100px;margin:0 auto;padding:30px}
h1{letter-spacing:.03em}small{color:#9fb1c8}.event{background:#162238;border:1px solid #31415b;border-radius:12px;padding:15px;margin:10px 0}
.row{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap}b{color:#8bd2ff}.empty{color:#c0cde0}
</style><h1>FUNDTEX / AGENT ACTIVITY</h1><p><small>Read-only local event trace. Only host-emitted events appear; absence of events means no verified activity.</small></p>
<div id="events"><p class="empty">No events observed.</p></div>
<script>async function refresh(){try{let r=await fetch("/events",{cache:"no-store"});if(!r.ok)throw Error("offline");
let list=await r.json(),root=document.getElementById("events");root.replaceChildren();
if(!list.length){let p=document.createElement("p");p.className="empty";p.textContent="No host-emitted events yet.";root.append(p);return;}
for(let e of list.slice().reverse()){let c=document.createElement("div");c.className="event";
let row=document.createElement("div");row.className="row";let a=document.createElement("b");a.textContent=e.agent+" / "+e.event;
let t=document.createElement("small");t.textContent=e.status+" | "+e.timestamp_utc;
row.append(a,t);let d=document.createElement("p");d.textContent=e.detail||"Lifecycle event";c.append(row,d);root.append(c);}
}catch{document.getElementById("events").textContent="Local trace temporarily unavailable.";}}
refresh();setInterval(refresh,2000);</script></html>"""

def view(path, *, port=8736, open_browser=False):
    target = _file(path)
    if not isinstance(port, int) or not 0 <= port <= 65535:
        raise ValueError("Port must be 0..65535")
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/events":
                try:
                    data = json.dumps(read_events(target), ensure_ascii=True).encode("ascii")
                    code = 200
                except (ValueError, OSError):
                    data = b'{"error":"event_log_unavailable"}'
                    code = 503
                media = "application/json; charset=utf-8"
            elif self.path == "/":
                data = _PAGE.encode("utf-8")
                code = 200
                media = "text/html; charset=utf-8"
            else:
                self.send_error(404); return
            self.send_response(code)
            self.send_header("Content-Type", media)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'none'; connect-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'")
            self.end_headers()
            self.wfile.write(data)
        def log_message(self, *_): pass
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    address = f"http://127.0.0.1:{server.server_port}/"
    print(json.dumps({"status":"SERVING_LOCAL_ACTIVITY","url":address,
                      "host":"127.0.0.1","has_agent_instrumentation":False,
                      "note":"Events appear only when host agents invoke activity-log"}), flush=True)
    if open_browser: webbrowser.open(address)
    try:
        server.serve_forever(poll_interval=0.25)
    finally:
        server.server_close()
