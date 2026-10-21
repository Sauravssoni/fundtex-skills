#!/usr/bin/env bash
# Install Fundtex + original trader skills. Never overwrite existing user files.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills"
python3 -c 'import sys; assert sys.version_info >= (3,9), "Fundtex requires Python >=3.9"'
mkdir -p "$DEST"
added=0
skipped=0
for skill in "$ROOT"/trader-* "$ROOT"/fundtex-*; do
  [[ -d "$skill" && -f "$skill/SKILL.md" ]] || continue
  name="$(basename "$skill")"
  if [[ -e "$DEST/$name" ]]; then
    printf 'SKIP  %s already exists\n' "$name"
    skipped=$((skipped+1))
  else
    cp -R "$skill" "$DEST/$name"
    printf 'ADD   %s\n' "$name"
    added=$((added+1))
  fi
done
printf '\nFundtex ready: installed=%s skipped=%s\n' "$added" "$skipped"
printf 'Run India engine from repository: python3 -m fundtex_india.cli --help\n'
printf 'Restart Claude Code to discover skills. No API keys required for CSV analysis.\n'
