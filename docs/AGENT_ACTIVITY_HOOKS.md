# Fundtex Agent Activity Hooks — Opt-in local instrumentation (Claude Code / Codex)

Fundtex is **CLI-first**. A dashboard is an **optional, read-only local companion**, only when useful for actual agent execution, tool timing and specialist activity. These hooks are explicitly opt-in and do **not** capture the model's hidden reasoning, requests, prompts, transcripts, tool names, agent IDs or broker credentials. Every emitted detail is a short **static** label. The displayed host is the user-configured hook host, not a cryptographically proven identity.

References:
- Codex lifecycle hooks: https://learn.chatgpt.com/docs/hooks
- Claude Code hooks: https://claude.com/resources/articles/how-to-configure-hooks

## Privacy and security

Set `FUNDTEX_EVENT_OPT_IN=1` **in the actual coding agent environment** and `FUNDTEX_EVENT_LOG=/private/approved/fundtex-events.jsonl` to an absolute local file inside an owner-approved existing private directory. The bridge refuses relative paths, non-existent parent folders and symlink log paths, relies on append-only mode 0600 for newly created files, and never sends data off-device. Do not put secrets, client files, model prompts or broker account information in the log path. The hook accepts only one hardcoded host (`claude` or `codex`) and declared event; it **does not parse stdin at all**.

Run the hook manually for isolated testing (it stays silent and exits zero):
```bash
PYTHONPATH=/approved/path/to/fundtex-skills FUNDTEX_EVENT_OPT_IN=1 \
FUNDTEX_EVENT_LOG=/approved/private/fundtex-events.jsonl \
python3 -m fundtex_india.hook_bridge --host codex --event SessionStart
```

Then the optional viewer, separately launched with user permission:
```bash
python3 -m fundtex_india.cli activity-view --events /approved/private/fundtex-events.jsonl --port 8736 --open
```
It binds only `127.0.0.1` and does not scan the user's other CLI work or remote sessions. It will show **no events** until the genuine host invokes the hook.

## Codex (manual project-local integration, never auto-installed)

Inspect your existing `<repo>/.codex/hooks.json` first, and **merge carefully** rather than overwriting user-defined hooks. Current Codex supports `SessionStart`, `PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, `Stop`, `SessionEnd`. The host may ask for hook-trust review. An illustrative hook configuration, assuming `fundtex_india` is importable from the host Python runtime, is:

```json
{
  "description": "Optional sanitized Fundtex local activity trace (read-only)",
  "hooks": {
    "SessionStart": [{"hooks": [{"type":"command","command":"python3 -m fundtex_india.hook_bridge --host codex --event SessionStart","timeout":3}]}],
    "PreToolUse": [{"hooks": [{"type":"command","command":"python3 -m fundtex_india.hook_bridge --host codex --event PreToolUse","timeout":3}]}],
    "PostToolUse": [{"hooks": [{"type":"command","command":"python3 -m fundtex_india.hook_bridge --host codex --event PostToolUse","timeout":3}]}],
    "SubagentStart": [{"hooks": [{"type":"command","command":"python3 -m fundtex_india.hook_bridge --host codex --event SubagentStart","timeout":3}]}],
    "SubagentStop": [{"hooks": [{"type":"command","command":"python3 -m fundtex_india.hook_bridge --host codex --event SubagentStop","timeout":3}]}],
    "Stop": [{"hooks": [{"type":"command","command":"python3 -m fundtex_india.hook_bridge --host codex --event Stop","timeout":3}]}]
  }
}
```
After manually opting in, restart/reload Codex and inspect actual events; do not infer functionality from a JSON template alone.

## Claude Code (manual project-local integration, never auto-installed)

Claude Code documents the same lifecycle trigger names. Use `<repo>/.claude/settings.local.json` or your approved personal settings; **never silently overwrite settings**. Example single event group (repeat event-specific groups as needed):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {"type":"command","command":"python3 -m fundtex_india.hook_bridge --host claude --event PostToolUse","timeout":3}
        ]
      }
    ]
  }
}
```

Do not configure any hook that ingests sensitive stdin or sends it to a model/server: our bridge ignores the payload entirely. Verify that the installed Fundtex Python package is importable in the agent's hook environment; its separate optional MCP server is **not** required.

## Honest behavior

The instrumented host can emit session starts, tool starts/completions, subagent lifecycle and end-turn events. Hooks do **not** prove the external API response was authentic, that the hosted model did real research, what tool was called, the name of a specific subagent, or how much work was done. Because we don't copy hook payload, the viewer deliberately uses the host name + generic lifecycle event instead of identifying individual agent types or their work. A more detailed opt-in host adapter may be added after source-specific privacy reviews. If hooks don't execute, the viewer honestly stays empty.

## Release checks

Run `python3 -m unittest -v tests.test_fundtex_hook_bridge tests.test_fundtex_activity` and inspect a private local trace. A simple `MCPServer.list_tools()` check does not validate hooks; real host lifecycle QA is still required. Do not merge these hooks into production/global config without separate owner approval.
