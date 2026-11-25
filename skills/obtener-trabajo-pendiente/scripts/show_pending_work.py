#!/usr/bin/env python3
"""Fetch and safely present pending tasks without persisting API responses."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

LAUNCHER = Path("/root/.openclaw/workspace/skills/fourgeeks-api-common/scripts/run_api_get.py")
PAGE_SIZE = 100
LIST_PATH = "/v1/assignment/user/me/task"
TASK_TYPES = "PROJECT,EXERCISE,LESSON"

# Deliberately exclude user and assignment_telemetry, even when provided by API.
FIELDS = (
    ("task_status", "Estado de tarea"),
    ("revision_status", "Estado de revisión"),
    ("task_type", "Tipo"),
    ("cohort", "Cohorte"),
    ("associated_slug", "Identificador de contenido"),
    ("description", "Descripción"),
    ("instructions", "Instrucciones"),
    ("opened_at", "Fecha de apertura"),
    ("read_at", "Fecha de lectura"),
    ("delivered_at", "Fecha de entrega"),
    ("reviewed_at", "Fecha de revisión"),
    ("created_at", "Fecha de creación"),
    ("updated_at", "Fecha de actualización"),
    ("github_url", "GitHub"),
    ("live_url", "URL pública"),
)


def safe_error(stderr: str, fallback: str) -> str:
    """Keep only the sanitized final client diagnostic, not arbitrary output."""
    for line in reversed(stderr.splitlines()):
        value = line.strip()
        if value.startswith(("API request failed", "API request returned HTTP", "Error:", "Could not start")):
            return value
    return fallback


def call_api(path: str, params: list[str]) -> tuple[Any | None, str | None]:
    env = os.environ.copy()
    env["FOURGEEKS_API_OUTPUT_JSON"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, str(LAUNCHER), path,
             *[arg for param in params for arg in ("--param", param)]],
            env=env, capture_output=True, text=True, check=False,
        )
    except OSError:
        return None, "error de ejecución"
    if result.returncode:
        return None, safe_error(result.stderr, "error del cliente API")
    try:
        return json.loads(result.stdout), None
    except (json.JSONDecodeError, TypeError):
        return None, "respuesta JSON no válida"


def extract_page(payload: Any) -> tuple[list[dict[str, Any]], int | None, bool]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)], None, False
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ValueError("formato de listado no reconocido")
    count = payload.get("count")
    if not isinstance(count, int) or count < 0:
        raise ValueError("respuesta paginada sin count válido")
    return [x for x in payload["results"] if isinstance(x, dict)], count, payload.get("next") is not None


def get_all_tasks() -> tuple[list[dict[str, Any]], bool, str | None]:
    tasks: list[dict[str, Any]] = []
    offset = 0
    while True:
        payload, error = call_api(LIST_PATH, [f"task_type={TASK_TYPES}", f"limit={PAGE_SIZE}", f"offset={offset}"])
        if error:
            return tasks, offset == 0, error
        try:
            page, count, has_next = extract_page(payload)
        except ValueError as exc:
            return tasks, offset == 0, str(exc)
        tasks.extend(page)
        # List response is not proof of completeness when pagination was requested.
        if count is None:
            return tasks, False, "paginación no verificable"
        if not page and offset < count:
            return tasks, False, "página vacía antes del final anunciado"
        offset += len(page)
        if offset >= count:
            return tasks, False, None
        if not has_next:
            return tasks, False, "la API no indicó la página siguiente antes del final anunciado"


def get_detail(task_id: Any) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(task_id, (int, str)) or not re.fullmatch(r"[0-9]+", str(task_id)):
        return None, "identificador no disponible o no válido"
    payload, error = call_api(f"/v1/assignment/task/{task_id}", [])
    if error:
        return None, error
    if not isinstance(payload, dict):
        return None, "formato de detalle no reconocido"
    return payload, None


def is_pending(item: dict[str, Any]) -> bool:
    return item.get("task_status") == "PENDING"


def is_unknown_status(item: dict[str, Any]) -> bool:
    status = item.get("task_status")
    # The API's TaskStatus enum currently defines only PENDING and DONE.
    # APPROVED/REJECTED belong to revision_status, not task_status.
    return status is None or status == "" or not isinstance(status, str) or status not in {
        "PENDING", "DONE"
    }


def fmt_value(value: Any) -> str:
    if isinstance(value, dict):
        # Cohort serializer fields only; prevent unrelated nested values leaking.
        parts = [str(value[k]) for k in ("name", "slug", "id") if value.get(k) not in (None, "")]
        return " — ".join(parts) if parts else "no disponible"
    if isinstance(value, (list, tuple)):
        return ", ".join(fmt_value(x) for x in value) or "no disponible"
    if value is None or value == "":
        return "no disponible"
    return str(value)


def title_of(item: dict[str, Any]) -> str:
    title = item.get("title")
    return str(title) if title not in (None, "") else "no identificada"


def id_text(item: dict[str, Any]) -> str:
    value = item.get("id")
    return f" (ID: {value})" if value not in (None, "") else ""


def render(tasks: list[dict[str, Any]], incomplete: bool, initial_error: bool, list_error: str | None) -> str:
    if initial_error:
        return f"No se pudo recuperar el listado de tareas ({list_error or 'error no disponible'})."

    pending = [task for task in tasks if is_pending(task)]
    unknown = [task for task in tasks if is_unknown_status(task)]
    lines: list[str] = []

    lines.append("## Resumen de tareas pendientes")
    if pending:
        for task in pending:
            cohort = fmt_value(task.get("cohort")) if task.get("cohort") else "no disponible"
            kind = fmt_value(task.get("task_type"))
            lines.append(f"- {title_of(task)}{id_text(task)} — Tipo: {kind} — Cohorte: {cohort}")
    elif not incomplete:
        lines.append("No tienes tareas pendientes")
    else:
        lines.append("No se pudieron determinar todas las tareas pendientes porque el listado está incompleto.")

    if pending:
        lines.append("\n## Detalle de tareas pendientes")
        for listed in pending:
            task = dict(listed)
            detail, error = get_detail(listed.get("id"))
            if detail is not None:
                # Only explicitly selected, non-personal fields are merged.
                task.update({k: v for k, v in detail.items() if k not in {"user", "assignment_telemetry"}})
            lines.append(f"\n### {title_of(task)}{id_text(task)}")
            for field, label in FIELDS:
                lines.append(f"- {label}: {fmt_value(task.get(field))}")
            # The API schema has no stable explicit remaining-steps field.
            has_guidance = any(task.get(k) not in (None, "") for k in ("instructions", "description"))
            if not has_guidance:
                lines.append("- Qué falta por hacer: la información disponible no permite determinarlo.")
            if error:
                lines.append("- No se pudo obtener el detalle de esta tarea")
                lines.append(f"- Error: {error}")

    if unknown:
        lines.append("\n## Estado no identificar")
        for task in unknown:
            status = task.get("task_status")
            status_text = "Sin estado" if status in (None, "") else str(status)
            lines.append(f"\n### {title_of(task)}{id_text(task)}")
            lines.append(f"- Estado: {status_text}")
            for field, label in FIELDS:
                if field == "task_status":
                    continue
                lines.append(f"- {label}: {fmt_value(task.get(field))}")

    if incomplete:
        lines.append(f"\n⚠️ El listado está incompleto; no se puede confirmar el conjunto total ({list_error or 'error no disponible'}).")
    return "\n".join(lines)


def main() -> int:
    tasks, initial_error, error = get_all_tasks()
    incomplete = error is not None
    print(render(tasks, incomplete, initial_error, error))
    return 1 if incomplete else 0


if __name__ == "__main__":
    raise SystemExit(main())
