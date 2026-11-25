# Academic tracking

Only retain academic information necessary to support Lourdes's training continuity. Do not store unnecessary personal information or confidential academy information. Do not treat access to material for a requested task as permission to retain it; ask if uncertain. Do not mark any task complete unless Lourdes confirms completion.

## Current course work

Course: AI Engineer training. The following work was reported by Lourdes as pending on 2026-11-21. No completion is implied; update status only from her confirmations.

- Topic 1: Project Milestone — AI-driven Engineering — pending.
- Topic 2: Project Hito 1 — Sitio web público de tu empresa — pending.
- Topic 5: Coding Fundamentals with TypeScript — 8 points pending.
- Topic 6:
  - Project: Mi Agente, A Mi Manera: Enseñando Nuevas Skills a Tu Asistente Personal — pending.
  - Module 2 — entire module pending; 3 points remain, plus project `Mi Asistente 4Geeks. Enseñándole a OpenClaw a seguir tu progreso` — pending.
- Topic 7: Module 1 — entire module pending, including project `Especificaciones y prototipo guiado por prompts de AgentHub` — pending.

## Shared 4Geeks API client
<!-- project: github.com/4GeeksAcademy/openclaw-LourdesAliste --> As of 2026-11-24, the common read-only client is in `skills/fourgeeks-api-common/`. `scripts/run_api_get.py` reads `TOKEN_4GEEKS` from the existing `/root/.openclaw/.env` (file remains unchanged) and passes it to `scripts/api_get.py` for that child process; no persistent token copy is created. The client only permits allowlisted GET routes, blocks redirects, validates TLS, and suppresses response bodies. Offline tests passed (six tests); a live `GET /v1/admissions/user/me` later succeeded with the response body suppressed. Four existing skills have not been integrated. Never store or reveal the token value. Continue by reviewing this common layer before integrating the four skills.

## Tracking conventions

- Track task status (pending / in progress / completed), confirmed progress and remaining work, blockers or concepts to reinforce, next steps and due dates, and topics studied or still pending.
- Lourdes will provide new academy lessons, tasks, deadlines, and dependency information; do not access the academy platform.
- No study hours are tracked. No task is completed until Lourdes confirms it.
