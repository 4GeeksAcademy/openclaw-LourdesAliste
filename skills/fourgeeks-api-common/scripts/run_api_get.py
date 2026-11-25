#!/usr/bin/env python3
"""Read the configured token from the original private env file and launch the GET client."""
from __future__ import annotations

import os
import re
import stat
import subprocess
import sys
from pathlib import Path

ENV_FILE = Path("/root/.openclaw/.env")
CLIENT = Path(__file__).with_name("api_get.py")


def read_token(path: Path = ENV_FILE) -> str:
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
        raise ValueError("credential file must be a private regular file owned by the current user")
    raw = path.read_text(encoding="utf-8")
    for line in raw.splitlines():
        candidate = line.strip()
        if candidate.startswith("export "):
            candidate = candidate[7:].lstrip()
        key, sep, value = candidate.partition("=")
        if sep and key.strip() == "TOKEN_4GEEKS":
            token = value.strip()
            if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
                token = token[1:-1]
            if not token or "\n" in token or "\r" in token:
                raise ValueError("credential is empty or malformed")
            return token
    raise ValueError("TOKEN_4GEEKS is not defined")


def main() -> int:
    try:
        token = read_token()
    except (OSError, UnicodeError, ValueError):
        print("Credential unavailable: check the private env file and TOKEN_4GEEKS definition.", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env["TOKEN_4GEEKS"] = token
    del token
    if os.environ.get("FOURGEEKS_API_OUTPUT_JSON") == "1":
        env["FOURGEEKS_API_OUTPUT_JSON"] = "1"
    else:
        env.pop("FOURGEEKS_API_OUTPUT_JSON", None)
    try:
        return subprocess.run([sys.executable, str(CLIENT), *sys.argv[1:]], env=env, check=False).returncode
    except OSError:
        print("Could not start the shared API client.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
