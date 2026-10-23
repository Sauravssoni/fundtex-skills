"""Read-only, pinned-source aware CLI update reconnaissance.

Reports whether a selected GitHub branch actually descends from the installed
commit; never fetches/executes remote code, replaces files or auto-upgrades.
Normal research/doctor commands must remain network-free by default.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

REPO="Sauravssoni/fundtex-skills"
COMMIT_RE=re.compile(r"^[a-fA-F0-9]{40}$")
REF_RE=re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._/-]{0,110}$")
API="https://api.github.com/repos/"+REPO
def _get(url, fetch=None):
    if fetch is not None:
        return fetch(url)
    request=urllib.request.Request(url,headers={"Accept":"application/vnd.github+json",
                           "User-Agent":"FundtexReadOnlyVersionChecker/1.0"})
    with urllib.request.urlopen(request,timeout=7) as response:
        if response.status!=200:
            raise ValueError("GitHub update service returned non-success status")
        blob=response.read(300_001)
    if len(blob)>300_000:raise ValueError("Update response too large")
    return json.loads(blob)

def check(*,ref="main",home=None,online=False,fetch=None):
    if not isinstance(ref,str) or not REF_RE.fullmatch(ref) or ".." in ref or "//" in ref:
        raise ValueError("Invalid GitHub ref for update check")
    local=Path(home).expanduser() if home else Path.home()
    marker=local/".local/share/fundtex-intelligence/.installed_source_commit"
    installed=None
    if marker.is_file() and marker.stat().st_size<=100:
        raw=marker.read_text(encoding="ascii").strip()
        if COMMIT_RE.fullmatch(raw):installed=raw.lower()
    out={"engine":"FUNDTEX_UPDATE_RECON_v1","repository":REPO,"selected_ref":ref,
         "installed_commit":installed,"read_only":True,
         "automatic_install":False,"user_approval_required_for_upgrade":True,
         "source_origin_authenticated_only_to_github_https":True}
    if not online:
        out.update({"status":"OFFLINE_NOT_CHECKED","note":"Agent may run fundtex updates --check only with network permission; no implicit polling."})
        return out
    try:
        remote=_get(API+"/commits/"+urllib.parse.quote(ref,safe=""),fetch=fetch)
        head=remote.get("sha")
        if not isinstance(head,str) or not COMMIT_RE.fullmatch(head):
            raise ValueError("Remote commit identity invalid")
        out["remote_head_commit"]=head
        out["remote_commit_url"]="https://github.com/"+REPO+"/commit/"+head
        if not installed:
            out["status"]="INSTALLED_SOURCE_UNKNOWN"
            out["note"]="No trusted installed commit marker; do not claim the remote is an upgrade"
        elif installed==head.lower():
            out["status"]="UP_TO_DATE_FOR_SELECTED_REF"
        else:
            compare=_get(API+"/compare/"+installed+"..."+head,fetch=fetch)
            state=compare.get("status")
            if state=="ahead":
                out["status"]="UPDATE_AVAILABLE_FOR_SELECTED_REF"
                out["commits_behind"]=compare.get("ahead_by")
            elif state=="behind":
                out["status"]="INSTALLED_NEWER_THAN_SELECTED_REF"
            elif state=="diverged":
                out["status"]="BRANCH_DIVERGED_REVIEW_REQUIRED"
            elif state=="identical":
                out["status"]="UP_TO_DATE_FOR_SELECTED_REF"
            else:
                raise ValueError("GitHub ancestry not independently validated")
        out["next_action"]="Show exact commit/diff; install only from an explicitly approved reviewed checkout using bash install.sh --upgrade. Never run arbitrary web scripts."
    except (OSError,ValueError,KeyError,TypeError,UnicodeError,TimeoutError) as exc:
        out["status"]="UPDATE_CHECK_FAILED_CLOSED"
        out["note"]="Could not verify ancestry or remote commit; no installation or fallback performed"
    return out
