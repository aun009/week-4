# haunted-shell 👻

`haunted-shell` is a tiny, local-first shell hook that whispers darkly funny comments about commands you run. Its curated rule library handles common commands without a model; unfamiliar commands can use a local Ollama model and are then cached. No API key, telemetry, or cloud call is required.

> Demo media: run `./demo.sh` and record the terminal; add the resulting GIF here before publishing.

## Install

```bash
git clone <your-repo-url> haunted-shell && cd haunted-shell
./install.sh                 # add --with-model to pull llama3.2:3b with Ollama
```

Restart your shell or run `source ~/.zshrc` / `source ~/.bashrc`. Test it safely with:

```bash
python3 haunt.py --test "sudo ls"
```

## Configuration

| Variable | Meaning |
| --- | --- |
| `HAUNT_INTENSITY=0..100` | Chance that a command receives a whisper (default: `35`). |
| `HAUNT_MODEL=qwen2.5:3b` | Optional Ollama model for unknown commands (default: `llama3.2:3b`). |
| `HAUNT_OFF=1` | Disable the hook for the current shell. |

It silently skips CI, non-interactive/no-terminal situations, and likely secrets (`password`, `token`, private keys, `AWS_`, and similar). Output goes straight to `/dev/tty`, never stdout, so pipes and redirected command output stay clean.

## Uninstall

```bash
./uninstall.sh
```

This removes only the marked hook block from Bash and Zsh RC files, and can remove the local cache.

## How it works

```text
shell command → privacy guard → whispers.json → cached local Ollama fallback → /dev/tty
```

The first matching rule wins. Unknown commands hash to `~/.cache/haunted-shell/cache.json`; the same unknown command is never inferred twice. `haunt.py` uses only Python's standard library and contacts only `localhost:11434` when an optional Ollama fallback is needed.

## Why open source matters

A terminal hook sees everything, so it should not phone home with command history. haunted-shell runs offline after setup, has a deliberate secret-pattern guard, and keeps its cache on the user's machine. The model is replaceable with one environment variable and can be fine-tuned independently; it cannot be repriced, deprecated, or taken away by a vendor. A closed hosted API would meter every whisper and make private shell history someone else's data problem.

The local rule library also keeps most responses at zero inference cost. The optional open-weight model provides a creative fallback without turning a joke into a subscription.

## License

[MIT](LICENSE)
