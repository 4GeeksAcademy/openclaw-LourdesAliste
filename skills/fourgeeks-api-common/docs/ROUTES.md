# Read-only route allowlist

Base URL: `https://breathecode.herokuapp.com` (confirm with the academy if the deployment differs).

Permitted GET paths:

- `/v1/admissions/user/me`
- `/v1/admissions/academy/cohort/me`
- `/v1/assignment/user/me/task`
- `/v1/assignment/task/{task_id}` — numeric identifier only
- `/v1/activity/me`
- `/v1/registry/asset`
- `/v1/registry/asset/{asset_slug}` — one path segment
- `/v1/registry/asset/me`
- `/v1/registry/technology`
- `/v1/events/all`

Query parameters are URL encoded by the client. Use documented filters and pagination sparingly. Routes omitted here are not available through this client. In particular, do not use task update/delivery endpoints or login endpoints.

The allowlist is intentionally conservative and should be extended only after reviewing the API documentation and the use case of the four skills.

## In-memory JSON output (trusted callers only)

By default, successful response bodies are suppressed. A trusted internal program may set `FOURGEEKS_API_OUTPUT_JSON=1` in the child-process environment to receive validated JSON on stdout for immediate in-memory processing. The launcher forwards this opt-in only when explicitly set. Never enable it for interactive shell output or logs; capture stdout directly in memory, do not persist/echo it, and never surface personal fields or telemetry. HTTP error bodies remain suppressed in all modes. This flag is not a secret-protection mechanism and must not be enabled in an untrusted environment.
