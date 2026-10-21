#!/usr/bin/env bash
# One-shot, safe and idempotent Claude Code skills + command-line installation.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills"
CODEX_DEST="$HOME/.codex/skills"
AGENTS_DEST="$HOME/.agents/skills"
DATA="$HOME/.local/share/fundtex-intelligence"
BIN="$HOME/.local/bin"
python3 -c 'import sys; assert sys.version_info >= (3,9), "Fundtex requires Python >=3.9"'
mkdir -p "$DEST" "$CODEX_DEST" "$AGENTS_DEST" "$DATA" "$BIN"
added=0
skipped=0
for dest in "$DEST" "$CODEX_DEST" "$AGENTS_DEST"; do
  printf 'TARGET %s\n' "$dest"
  for skill in "$ROOT"/trader-* "$ROOT"/fundtex-*; do
    [[ -d "$skill" && -f "$skill/SKILL.md" ]] || continue
    name="$(basename "$skill")"
    if [[ -e "$dest/$name" ]]; then
      printf 'SKIP  %s already exists\n' "$name"
      skipped=$((skipped+1))
    else
      cp -R "$skill" "$dest/$name"
      printf 'ADD   %s\n' "$name"
      added=$((added+1))
    fi
  done
done
if [[ ! -e "$DATA/fundtex_india" ]]; then
  cp -R "$ROOT/fundtex_india" "$DATA/fundtex_india"
  printf 'ADD   local India analysis engine\n'
else
  printf 'SKIP  existing India engine; upgrade requires explicit replacement\n'
fi
if [[ ! -e "$BIN/fundtex" ]]; then
  cat > "$BIN/fundtex" <<'EOF'
#!/usr/bin/env bash
PYTHONPATH="$HOME/.local/share/fundtex-intelligence" python3 -m fundtex_india.cli "$@"
EOF
  chmod 755 "$BIN/fundtex"
  printf 'ADD   ~/.local/bin/fundtex launcher\n'
else
  printf 'SKIP  existing launcher; not overwritten\n'
fi
printf '\nFundtex ready: skills installed=%s skipped=%s\n' "$added" "$skipped"
printf 'Run: "$HOME/.local/bin/fundtex" --help\n'
printf 'Restart Claude/Codex to discover skills. No credentials required for CSV analysis.\n'
