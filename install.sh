#!/usr/bin/env bash
# One-shot, safe and idempotent Claude Code skills + command-line installation.
set -euo pipefail
UPGRADE=0
for flag in "$@"; do
  case "$flag" in
    --upgrade) UPGRADE=1 ;;
    *) printf "Unknown installer option: %s\\nUse --upgrade only after explicit approval.\\n" "$flag" >&2; exit 2 ;;
  esac
done
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
replaced=0
backup=""
if [[ "$UPGRADE" -eq 1 ]]; then
  backup="$(mktemp -d "$DATA/fundtex-backup-XXXXXXXX")"
  printf "Upgrade explicitly approved. Previous files saved at %s\\n" "$backup"
fi
index=0
for dest in "$DEST" "$CODEX_DEST" "$AGENTS_DEST"; do
  printf 'TARGET %s\n' "$dest"
  index=$((index+1))
  for skill in "$ROOT"/trader-* "$ROOT"/fundtex-*; do
    [[ -d "$skill" && -f "$skill/SKILL.md" ]] || continue
    name="$(basename "$skill")"
    if [[ -e "$dest/$name" && "$UPGRADE" -eq 1 ]]; then
      stage="$dest/.$name.fundtex-next.$$"
      cp -R "$skill" "$stage"
      mv "$dest/$name" "$backup/agent-$index-$name"
      if ! mv "$stage" "$dest/$name"; then
        mv "$backup/agent-$index-$name" "$dest/$name"
        printf "Skill upgrade failed; original restored: %s\\n" "$name" >&2
        exit 1
      fi
      printf 'UPDATE %s (backup saved)\n' "$name"
      replaced=$((replaced+1))
    elif [[ -e "$dest/$name" ]]; then
      printf 'SKIP  %s already exists\n' "$name"
      skipped=$((skipped+1))
    else
      cp -R "$skill" "$dest/$name"
      printf 'ADD   %s\n' "$name"
      added=$((added+1))
    fi
  done
done
if [[ -e "$DATA/fundtex_india" && "$UPGRADE" -eq 1 ]]; then
  stage="$DATA/.fundtex-engine-next.$$"
  cp -R "$ROOT/fundtex_india" "$stage"
  mv "$DATA/fundtex_india" "$backup/fundtex_india"
  if ! mv "$stage" "$DATA/fundtex_india"; then
    mv "$backup/fundtex_india" "$DATA/fundtex_india"
    echo "Engine upgrade failed; original restored" >&2
    exit 1
  fi
  printf 'UPDATE India analysis engine (backup saved)\n'
elif [[ ! -e "$DATA/fundtex_india" ]]; then
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
printf '\nFundtex ready: skills installed=%s skipped=%s updated=%s\n' "$added" "$skipped" "$replaced"
printf 'Run: "$HOME/.local/bin/fundtex" --help\n'
printf 'Restart Claude/Codex to discover skills. No credentials required for CSV analysis.\n'
PYTHONPATH="$ROOT" python3 -m fundtex_india.onboarding
printf 'Agent-ready: ask Claude/Codex to analyze an Indian company; Fundtex will handle commands and exports.\n'
printf 'Agent-side one-shot: "%s/fundtex" research --symbol INFY.NS --source public --out /new/report-directory\n' "$BIN"
if [[ "$UPGRADE" -eq 1 ]]; then printf 'Previous versions preserved: %s\n' "$backup"; fi
