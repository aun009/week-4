#!/usr/bin/env bash
set -euo pipefail
for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
  [ -f "$rc" ] || continue
  tmp="$(mktemp)"
  awk '/# haunted-shell BEGIN/{skip=1; next} /# haunted-shell END/{skip=0; next} !skip' "$rc" > "$tmp"
  mv "$tmp" "$rc"
  echo "Removed hook from $rc"
done
cache="$HOME/.cache/haunted-shell"
if [ -d "$cache" ] && [ -t 0 ]; then
  read -r -p "Delete cached local whispers? [y/N] " answer
  [ "${answer:-N}" = y ] || [ "${answer:-N}" = Y ] || exit 0
  rm -rf "$cache"
  echo "Deleted $cache"
fi
