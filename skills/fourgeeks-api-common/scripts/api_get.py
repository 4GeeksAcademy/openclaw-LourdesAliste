#!/usr/bin/env python3
"""Minimal read-only client for explicitly allowlisted 4Geeks API GET routes."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE_URL = "https://breathecode.herokuapp.com"
TIMEOUT_SECONDS = 20
MAX_RESPONSE_BYTES = 2_000_000


def is_allowed(path: str) -> bool:
    if not path.startswith("/") or "?" in path or "#" in path or "\\" in path:
        return False
    if re.search(r"%2f|%5c|%2e", path, re.IGNORECASE) or ".." in path:
        return False
    fixed = {
        "/v1/admissions/user/me",
        "/v1/admissions/academy/cohort/me",
        "/v1/assignment/user/me/task",
        "/v1/activity/me",
        "/v1/registry/asset",
        "/v1/registry/asset/me",
        "/v1/registry/technology",
        "/v1/events/all",
    }
    if path in fixed:
        return True
    if re.fullmatch(r"/v1/assignment/task/[0-9]+", path):
        return True
    if re.fullmatch(r"/v1/assignment/me/task/[0-9]+/coderevision", path):
        return True
    if re.fullmatch(r"/v1/registry/asset/[A-Za-z0-9_-]+", path):
        return path != "/v1/registry/asset/me"
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="allowlisted API path")
    parser.add_argument("--param", action="append", default=[], metavar="KEY=VALUE")
    args = parser.parse_args()

    if not is_allowed(args.path):
        print("Error: path is not on the read-only allowlist.", file=sys.stderr)
        return 2
    token = os.environ.get("TOKEN_4GEEKS")
    if not token:
        print("Error: TOKEN_4GEEKS is unavailable; invoke the shared run_api_get.py launcher.", file=sys.stderr)
        return 2
    query: list[tuple[str, str]] = []
    for item in args.param:
        key, sep, value = item.partition("=")
        if not sep or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            print("Error: each --param must be KEY=VALUE with a simple key.", file=sys.stderr)
            return 2
        query.append((key, value))
    url = BASE_URL + args.path
    if query:
        url += "?" + urlencode(query)
    # Fixed HTTPS host, no redirects, no caller-supplied headers or methods.
    request = Request(url, headers={"Authorization": "Token " + token, "Accept": "application/json"}, method="GET")
    del token
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opener = build_opener(NoRedirect)
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            if response.geturl() != url or urlsplit(response.geturl()).hostname != "breathecode.herokuapp.com":
                print("Error: unexpected response destination; request stopped.", file=sys.stderr)
                return 1
            body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                print("Error: response exceeded the 2 MB safety limit.", file=sys.stderr)
                return 1
            charset = response.headers.get_content_charset() or "utf-8"
            text = body.decode(charset, errors="replace")
            try:
                json.loads(text)
            except json.JSONDecodeError:
                print("Error: API response was not valid JSON.", file=sys.stderr)
                return 1
            # Bodies remain suppressed unless an explicitly opted-in caller needs
            # them for in-memory processing. Never log or echo them.
            if os.environ.get("FOURGEEKS_API_OUTPUT_JSON") == "1":
                sys.stdout.write(text)
                sys.stdout.write("\n")
            else:
                print("API request succeeded (HTTP response was valid JSON; body suppressed).")
            return 0
    except HTTPError as exc:
        if 300 <= exc.code < 400:
            print(f"API request returned HTTP {exc.code}; redirects are blocked.", file=sys.stderr)
        else:
            print(f"API request failed with HTTP {exc.code}; response body suppressed.", file=sys.stderr)
    except (URLError, TimeoutError, OSError):
        print("API request failed due to a network or timeout error; details suppressed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
