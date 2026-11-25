#!/usr/bin/env python3
"""Fetch and present the authenticated user's projects without persisting API data."""
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


def call_api(path: str, params: list[str]) -> tuple[Any | None, str | None]:
    env = os.environ.copy()
    env["FOURGEEKS_API_OUTPUT_JSON"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, str(LAUNCHER), path, *[arg for p in params for arg in ("--param", p)]],
            env=env, capture_output=True, text=True, check=False,
        )
    except OSError:
        return None, "error de ejecución"
    if result.returncode:
        # The shared client emits only a sanitized HTTP/network/validation reason.
        safe = result.stderr.strip().splitlines()
        return None, safe[-1] if safe else "error del cliente API"
    try:
        return json.loads(result.stdout), None
    except (json.JSONDecodeError, TypeError):
        return None, "respuesta JSON no válida"


def extract_page(payload: Any) -> tuple[list[dict[str, Any]], int | None, bool]:
    if isinstance(payload, list):
        return payload, None, False
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ValueError("formato de listado no reconocido")
    count = payload.get("count")
    if not isinstance(count, int) or count < 0:
        raise ValueError("respuesta paginada sin count válido")
    return payload["results"], count, payload.get("next") is not None


def get_projects() -> tuple[list[dict[str, Any]], bool, str | None]:
    items: list[dict[str, Any]] = []
    offset = 0
    while True:
        payload, error = call_api("/v1/assignment/user/me/task", [
            "task_type=PROJECT", f"limit={PAGE_SIZE}", f"offset={offset}",
        ])
        if error:
            return items, offset == 0, error
        try:
            page, count, has_next = extract_page(payload)
        except ValueError as exc:
            return items, offset == 0, str(exc)
        items.extend(x for x in page if isinstance(x, dict))
        if count is None:  # Plain list: not paginated; its completeness cannot be verified.
            return items, False, "paginación no verificable"
        offset += len(page)
        if offset >= count or not has_next:
            return items, False, None
        if not page:
            return items, False, "página vacía antes del final anunciado"


def detail(task_id: Any) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(task_id, (int, str)) or not re.fullmatch(r"[0-9]+", str(task_id)):
        return None, "identificador no disponible o no válido"
    payload, error = call_api(f"/v1/assignment/task/{task_id}", [])
    if error:
        return None, error
    if not isinstance(payload, dict):
        return None, "formato de detalle no reconocido"
    return payload, None


def status_bucket(item: dict[str, Any]) -> str:
    task = item.get("task_status")
    revision = item.get("revision_status")
    if task == "PENDING":
        return "Pendientes"
    if task == "DONE":
        if revision == "APPROVED":
            return "Aprobados"
        if revision == "REJECTED":
            return "Rechazados"
        if revision in (None, "PENDING", "IGNORED"):
            return "Entregados"
        return f"Estado no identificado: {revision}"
    if task == "APPROVED":
        return "Aprobados"
    if task == "REJECTED":
        return "Rechazados"
    return f"Estado no identificado: {task if task is not None else 'sin valor'}"


def present_value(label: str, value: Any) -> str | None:
    if value is None or value == "" or isinstance(value, (dict, list)):
        return None
    return f"  - {label}: {value}"


def render(items: list[dict[str, Any]], complete: bool, initial_error: bool, list_error: str | None) -> str:
    if initial_error:
        return f"No se han podido recuperar los proyectos ({list_error})."
    sections: dict[str, list[tuple[dict[str, Any], str | None]]] = {
        "Pendientes": [], "Entregados": [], "Aprobados": [], "Rechazados": [],
    }
    unknown: list[tuple[dict[str, Any], str | None, str]] = []
    for item in items:
        d, err = detail(item.get("id"))
        combined = {**item, **(d or {})}
        bucket = status_bucket(combined)
        if bucket in sections:
            sections[bucket].append((combined, err))
        else:
            unknown.append((combined, err, bucket))

    lines: list[str] = []
    for title in ("Pendientes", "Entregados", "Calificados — Aprobados", "Calificados — Rechazados"):
        key = title.split("— ")[-1] if "— " in title else title
        lines.append(f"## {title}")
        entries = sections[key]
        if not entries and complete:
            lines.append("No hay proyectos en este estado")
        for item, error in entries:
            lines.append(f"- {item.get('title') or item.get('associated_slug') or 'Proyecto sin título'}")
            for field, label in (("cohort", "Cohorte"), ("task_status", "Estado de tarea"),
                                 ("revision_status", "Estado de revisión"), ("opened_at", "Fecha de apertura"),
                                 ("delivered_at", "Fecha de entrega"), ("reviewed_at", "Fecha de revisión"),
                                 ("github_url", "GitHub"), ("live_url", "URL pública"),
                                 ("description", "Descripción")):
                value = item.get(field)
                if field == "cohort" and isinstance(value, dict):
                    value = value.get("name") or value.get("slug")
                text = present_value(label, value)
                if text:
                    lines.append(text)
            if error:
                lines.append(f"  - No se pudo obtener el detalle de este proyecto ({error}); no se recuperaron los campos disponibles solo en el detalle.")
    if unknown:
        lines.append("## Estados no identificados")
        for item, error, bucket in unknown:
            lines.append(f"- {item.get('title') or item.get('associated_slug') or 'Proyecto sin título'} — {bucket}")
            if error:
                lines.append(f"  - No se pudo obtener el detalle de este proyecto ({error}).")
    if list_error:
        lines.append(f"⚠️ La lista está incompleta; no se pudieron recuperar más proyectos ({list_error}).")
    return "\n".join(lines)


def main() -> int:
    items, initial_error, error = get_projects()
    complete = error is None and not initial_error
    print(render(items, complete, initial_error, error))
    return 1 if error else 0


if __name__ == "__main__":
    raise SystemExit(main())
