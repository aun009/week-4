#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
commands=("ls -la" "cd /tmp" "sudo ls /root" "git commit -m 'summon ghost'" "npm install" "docker ps" "rg haunted" "curl https://example.com" "chmod 777 cursed.txt" "rm -rf node_modules" "git push origin main --force" "exit")
for command in "${commands[@]}"; do
  printf '\n\033[1;32m$ %s\033[0m\n' "$command"
  "$ROOT/haunt.py" --test "$command" | sed 's/^/  👻 /'
  sleep 0.35
done
