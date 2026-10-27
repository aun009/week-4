#!/usr/bin/env python3
"""The local, privacy-first brain behind haunted-shell."""
import hashlib
import json
import os
import random
import re
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
CACHE_DIR = Path.home() / ".cache" / "haunted-shell"
CACHE_FILE = CACHE_DIR / "cache.json"
COOLDOWN_FILE = CACHE_DIR / "last.json"
FALLBACKS = ["I have seen this command before. In a dream.", "The terminal hums its disapproval.", "A familiar ritual. An unfamiliar consequence."]
SECRET = re.compile(r"password|token|apikey|api_key|secret|BEGIN.*PRIVATE KEY|AWS_", re.I)


def read_rules():
    with (ROOT / "whispers.json").open(encoding="utf-8") as source:
        return json.load(source)


def cache_read(path, default):
    try:
        with path.open(encoding="utf-8") as source:
            return json.load(source)
    except (OSError, ValueError):
        return default


def cache_write(path, value):
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(value), encoding="utf-8")
        temporary.replace(path)
    except OSError:
        # A read-only home directory should never break the shell hook.
        pass


def local_line(command, rules):
    for rule in rules["rules"]:
        if re.search(rule["pattern"], command, re.I):
            return random.choice(rule["lines"])
    return None


def ask_ollama(command, prompt):
    payload = json.dumps({"model": os.getenv("HAUNT_MODEL", "llama3.2:3b"), "system": prompt,
        "prompt": command, "stream": False, "options": {"temperature": 0.9, "num_predict": 30}}).encode()
    request = Request("http://localhost:11434/api/generate", data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=3) as response:
            line = json.loads(response.read())["response"].strip().replace("\n", " ")
            return line[:240] or random.choice(FALLBACKS)
    except (URLError, OSError, ValueError, KeyError):
        return random.choice(FALLBACKS)


def fallback_line(command, rules):
    key = hashlib.sha256(command.encode()).hexdigest()
    cache = cache_read(CACHE_FILE, {})
    if key not in cache:
        cache[key] = ask_ollama(command, rules["generic_prompt"])
        cache_write(CACHE_FILE, cache)
    return cache[key]


def allowed(command, force):
    if force:
        return True
    if os.getenv("HAUNT_OFF") == "1" or os.getenv("CI") or os.getenv("GITHUB_ACTIONS") or SECRET.search(command):
        return False
    try:
        fd = os.open("/dev/tty", os.O_WRONLY)
        os.close(fd)
    except OSError:
        return False
    intensity = max(0, min(100, int(os.getenv("HAUNT_INTENSITY", "35"))))
    if random.randrange(100) >= intensity:
        return False
    last = cache_read(COOLDOWN_FILE, {})
    now = time.time()
    if last.get("command") == command and now - last.get("at", 0) < 2:
        return False
    cache_write(COOLDOWN_FILE, {"command": command, "at": now})
    return True


def emit(line, test):
    if test:
        print(line)
        return
    try:
        with open("/dev/tty", "w", encoding="utf-8") as tty:
            tty.write("\033[2;3m  👻 " + line + "\033[0m\n")
    except OSError:
        pass


def main():
    test = len(sys.argv) > 1 and sys.argv[1] == "--test"
    command = " ".join(sys.argv[2:]) if test else (" ".join(sys.argv[1:]) or sys.stdin.read())
    command = command.strip()
    if not command or not allowed(command, test):
        return
    rules = read_rules()
    emit(local_line(command, rules) or fallback_line(command, rules), test)


if __name__ == "__main__":
    main()
