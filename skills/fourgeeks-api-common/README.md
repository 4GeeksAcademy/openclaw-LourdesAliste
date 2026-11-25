# 4Geeks API common client

Shared read-only GET client for the learning skills. Invoke `scripts/run_api_get.py`; it reads `TOKEN_4GEEKS` from the existing `/root/.openclaw/.env` and passes it to the client process without creating a persistent copy. It does not execute `.env` as shell code. The token is plaintext in process memory during use.

See `SKILL.md` for invocation and `docs/ROUTES.md` for the conservative allowlist. Tests are offline and use only a temporary fixture/dummy credential.
