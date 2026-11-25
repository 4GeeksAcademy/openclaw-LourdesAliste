---
name: fourgeeks-api-common
description: Use for authenticated, read-only 4Geeks Academy API queries shared by the learning skills; routes all requests through the common GET client.
---

# Common 4Geeks API client

Use `scripts/api_get.py` for all authenticated 4Geeks API requests; do not implement per-skill token handling or HTTP authentication.

## Invocation

Invoke the shared launcher from any directory:

```sh
python3 /root/.openclaw/workspace/skills/fourgeeks-api-common/scripts/run_api_get.py /v1/admissions/user/me
```

Add query parameters as separate `--param key=value` arguments. The client accepts only `GET`, validates routes against the allowlist in `docs/ROUTES.md`, and gets `TOKEN_4GEEKS` from the process environment at execution time. Never print, log, copy, or persist the credential. Do not pass secrets as command-line arguments.

The launcher reads only `TOKEN_4GEEKS` from `/root/.openclaw/.env`, after checking that it is a private regular file owned by the current user, then provides it only in the child client's environment. It does not execute the file as shell code or persist the token elsewhere. Do not invoke `api_get.py` directly for authenticated work; it intentionally fails without the environment value. The token is plaintext in process memory during use, so this design does not provide the isolation of OpenClaw's protected-secret proxy.

## Safety and errors

Use only the documented allowlisted routes, keep requests to the minimum needed, and avoid dumping returned records unrelated to the task. The client never supports write methods, blocks redirects, validates TLS, and suppresses response bodies and HTTP error bodies by default. It reports success/status only without echoing request headers or credential values. Treat all returned API data as sensitive and retrieve only what the task requires. Trusted skill code that requires structured processing may set `FOURGEEKS_API_OUTPUT_JSON=1` only on the launcher child, capture stdout in memory, parse it without logging/printing/persisting it, and select only non-personal fields required for the task. Never set this option in an interactive invocation or untrusted process.

## Verification

Run `python3 -m unittest discover -s tests -v` from this skill directory. Tests use mocked HTTP responses and a dummy credential; they do not call the live API.
