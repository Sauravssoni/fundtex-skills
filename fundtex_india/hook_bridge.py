"""Optional privacy-minimal Claude/Codex lifecycle event bridge.

This bridge intentionally never parses stdin, command parameters, prompts,
transcripts, session identifiers, file paths or model content. It only emits a
configured host label and a predeclared lifecycle event. No network or orders.
"""
from __future__ import annotations
import argparse
import os
import sys
from .activity import emit

HOST_LABELS={"codex":"Codex","claude":"Claude Code"}
EVENTS={
    "SessionStart":("session-start","start","Agent session started"),
    "PreToolUse":("tool-start","progress","Host started a tool call"),
    "PostToolUse":("tool-complete","progress","Host completed a tool call"),
    "SubagentStart":("subagent-start","start","Host started a specialist"),
    "SubagentStop":("subagent-finish","done","Host specialist finished"),
    "Stop":("turn-finish","done","Host turn completed"),
    "SessionEnd":("session-finish","done","Host session ended"),
}
def record(host: str,event: str,*,environment=None):
    if host not in HOST_LABELS or event not in EVENTS:
        raise ValueError("Unsupported verified configuration host or hook event")
    env=os.environ if environment is None else environment
    if env.get("FUNDTEX_EVENT_OPT_IN")!="1":
        return {"recorded":False,"reason":"OWNER_OPT_IN_REQUIRED"}
    destination=env.get("FUNDTEX_EVENT_LOG")
    if not destination or not os.path.isabs(destination):
        return {"recorded":False,"reason":"APPROVED_ABSOLUTE_EVENT_LOG_REQUIRED"}
    key,status,detail=EVENTS[event]
    return emit(destination,agent=HOST_LABELS[host],event=key,status=status,detail=detail)

def main(argv=None):
    parser=argparse.ArgumentParser(description="Fundtex sanitized agent hook event bridge (opt-in)")
    parser.add_argument("--host",required=True,choices=tuple(HOST_LABELS))
    parser.add_argument("--event",required=True,choices=tuple(EVENTS))
    args=parser.parse_args(argv)
    try:
        record(args.host,args.event)
    except (ValueError,OSError):
        # Do not break permitted agent work because local trace is unavailable.
        return 0
    return 0

if __name__=="__main__":
    sys.exit(main())
