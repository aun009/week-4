#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "${SHELL:-}" in
  */zsh) RC="$HOME/.zshrc"; SHELL_KIND=zsh ;;
  */bash) RC="$HOME/.bashrc"; SHELL_KIND=bash ;;
  *) echo "haunted-shell supports Bash and Zsh. Add a hook that calls: python3 '$ROOT/haunt.py' \"\$command\""; exit 0 ;;
esac
mkdir -p "$(dirname "$RC")"; touch "$RC"
tmp="$(mktemp)"
awk '/# haunted-shell BEGIN/{skip=1; next} /# haunted-shell END/{skip=0; next} !skip' "$RC" > "$tmp"
mv "$tmp" "$RC"
if [ "$SHELL_KIND" = zsh ]; then
  cat >> "$RC" <<EOF
# haunted-shell BEGIN
haunted_shell_preexec() {
  [ -n "\$COMP_LINE" ] && return
  printf '%s\\n' "\$1" | python3 "$ROOT/haunt.py" &
}
autoload -Uz add-zsh-hook 2>/dev/null && add-zsh-hook preexec haunted_shell_preexec
# haunted-shell END
EOF
else
  cat >> "$RC" <<EOF
# haunted-shell BEGIN
__haunted_prompt() {
  local cmd
  cmd=\$(HISTTIMEFORMAT= history 1 | sed 's/^ *[0-9]* *//')
  [ -n "\$cmd" ] && printf '%s\\n' "\$cmd" | python3 "$ROOT/haunt.py" &
}
PROMPT_COMMAND="__haunted_prompt\${PROMPT_COMMAND:+;\$PROMPT_COMMAND}"
# haunted-shell END
EOF
fi
chmod +x "$ROOT/haunt.py" "$ROOT/install.sh" "$ROOT/uninstall.sh" "$ROOT/demo.sh"
if [ "${1:-}" = "--with-model" ]; then
  if command -v ollama >/dev/null 2>&1; then ollama pull "${HAUNT_MODEL:-llama3.2:3b}"; else echo "Ollama is optional; install it from https://ollama.com then run: ollama pull llama3.2:3b"; fi
fi
echo "Installed in $RC. Activate with: source $RC"
