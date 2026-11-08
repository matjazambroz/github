#!/usr/bin/env bash
# Kopira agenta v ~/.claude (korak 1-5 s slike). Ne prepisuje obstoječega ~/CLAUDE.md brez vprašanja.
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
PROJECT="${1:-amidas-racunovodstvo}"
mkdir -p ~/.claude/agents ~/.claude/skills/prejeti-racuni ~/.claude/projects/"$PROJECT"/memory
cp "$SRC"/agents/*.md ~/.claude/agents/
mkdir -p ~/.claude/eslog && cp -r "$SRC"/eslog/. ~/.claude/eslog/
cp "$SRC"/evidenca-*.* ~/.claude/
cp "$SRC"/kontni-nacrt.md ~/.claude/kontni-nacrt.md
cp "$SRC"/skills/prejeti-racuni/SKILL.md ~/.claude/skills/prejeti-racuni/
cp -n "$SRC"/memory/*.md ~/.claude/projects/"$PROJECT"/memory/
if [ -e ~/CLAUDE.md ]; then
  echo "~/CLAUDE.md ze obstaja: vsebino iz accounting-agent/CLAUDE.md dodaj rocno (ali: cat >> ~/CLAUDE.md)."
else
  cp "$SRC"/CLAUDE.md ~/CLAUDE.md
fi
echo "Namesceno. Zazeni 'claude' in vpisi /prejeti-racuni. Rutine: glej routines.md."
