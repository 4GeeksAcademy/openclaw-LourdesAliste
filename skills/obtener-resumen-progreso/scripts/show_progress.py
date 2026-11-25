#!/usr/bin/env python3
"""Summarize assigned task progress and activity without persisting API payloads."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

LAUNCHER = Path("/root/.openclaw/workspace/skills/fourgeeks-api-common/scripts/run_api_get.py")
PAGE_SIZE = 100
LIST_PATH = "/v1/assignment/user/me/task"
TASK_TYPES = "PROJECT,EXERCISE,LESSON,QUIZ"
KNOWN_STATUSES = {"PENDING", "DONE"}
REVIEW_STATUSES = {"PENDING", "APPROVED", "REJECTED"}


def call_api(path: str, params: list[str] | None = None) -> tuple[Any | None, str | None]:
    env = os.environ.copy()
    env["FOURGEEKS_API_OUTPUT_JSON"] = "1"
    argv = [sys.executable, str(LAUNCHER), path]
    for param in params or []:
        argv.extend(("--param", param))
    try:
        result = subprocess.run(argv, env=env, capture_output=True, text=True, check=False)
    except OSError:
        return None, "error de ejecución"
    if result.returncode:
        # Preserve only the numeric HTTP status from the sanitized client message.
        match = re.search(r"API request failed with HTTP ([0-9]{3})", result.stderr)
        return None, f"HTTP {match.group(1)}" if match else "falló la consulta API"
    try:
        return json.loads(result.stdout), None
    except (json.JSONDecodeError, TypeError):
        return None, "respuesta JSON no válida"


def page_items(payload: Any) -> tuple[list[dict[str, Any]], int | None, bool]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)], None, False
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ValueError("formato no reconocido")
    count = payload.get("count")
    if not isinstance(count, int) or count < 0:
        raise ValueError("paginación sin count válido")
    return [x for x in payload["results"] if isinstance(x, dict)], count, payload.get("next") is not None


def get_tasks() -> tuple[list[dict[str, Any]], bool, str | None]:
    all_tasks: list[dict[str, Any]] = []
    offset = 0
    while True:
        payload, error = call_api(LIST_PATH, [f"task_type={TASK_TYPES}", f"limit={PAGE_SIZE}", f"offset={offset}"])
        if error:
            return all_tasks, False, error
        try:
            page, count, has_next = page_items(payload)
        except ValueError as exc:
            return all_tasks, False, str(exc)
        all_tasks.extend(page)
        if count is None:
            return all_tasks, False, "paginación no verificable"
        offset += len(page)
        if offset >= count:
            return all_tasks, True, None
        if not page or not has_next:
            return all_tasks, False, "paginación incompleta"


def scalar(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return None


def cohort_key(record: dict[str, Any]) -> str | None:
    value = record.get("cohort")
    if isinstance(value, dict):
        name = scalar(value.get("name"))
        slug = scalar(value.get("slug"))
        ident = scalar(value.get("id"))
        label = name or slug
        if label and ident:
            return f"{label} (ID: {ident})"
        return label or (f"ID: {ident}" if ident else None)
    return scalar(value)


def task_type(task: dict[str, Any]) -> str:
    return scalar(task.get("task_type")) or "Tipo no disponible"


def task_cohort(task: dict[str, Any]) -> str:
    return cohort_key(task) or "Cohorte no disponible"


def known_count(items: list[dict[str, Any]]) -> tuple[int, int, int]:
    return tuple(sum(1 for x in items if x.get("task_status") == status) for status in ("PENDING", "DONE", "UNKNOWN"))


def pct(done: int, pending: int) -> str:
    total = done + pending
    return f"{100 * done / total:.1f}% ({done}/{total})" if total else "Avance no disponible"


def render_tasks(tasks: list[dict[str, Any]], complete: bool, error: str | None) -> list[str]:
    lines = ["## Progreso de tareas"]
    if error:
        lines.append(f"Listado de tareas parcial o no disponible ({error}).")
    lines.append("Las cohortes se muestran solo cuando aparecen identificadas en las tareas; esta vista no enumera cohortes sin tareas ni garantiza una lista completa.")
    cohort_names: list[str] = []
    for task in tasks:
        key = task_cohort(task)
        if key != "Cohorte no disponible" and key not in cohort_names:
            cohort_names.append(key)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        groups[task_cohort(task)].append(task)
    if not tasks:
        lines.append("No hay tareas recuperadas." if complete else "No se recuperaron tareas; resultado incompleto.")
    for cohort in cohort_names + (["Cohorte no disponible"] if "Cohorte no disponible" in groups else []):
        items = groups.get(cohort, [])
        lines.append(f"\n### {cohort}")
        types = sorted({task_type(x) for x in items})
        for kind in types:
            typed = [x for x in items if task_type(x) == kind]
            pending, done, _ = known_count(typed)
            unknown = sum(1 for x in typed if x.get("task_status") not in KNOWN_STATUSES)
            lines.append(f"- {kind}: PENDING {pending}, DONE {done}; entregadas {pct(done, pending)}; estados ausentes/desconocidos {unknown}")
        pending, done, _ = known_count(items)
        unknown_items = [x for x in items if x.get("task_status") not in KNOWN_STATUSES]
        lines.append(f"- Total de tareas: PENDING {pending}, DONE {done}; entregadas {pct(done, pending)}; estados ausentes/desconocidos {len(unknown_items)}")
        if unknown_items:
            lines.append("- Tareas con estado no identificable:")
            for task in unknown_items:
                title = scalar(task.get("title")) or "no identificada"
                task_id = scalar(task.get("id"))
                status = scalar(task.get("task_status")) or "Sin estado"
                suffix = f" (ID: {task_id})" if task_id else ""
                lines.append(f"  - {title}{suffix} — Tipo: {task_type(task)} — Estado: {status}")
        projects = [x for x in items if task_type(x) == "PROJECT"]
        if projects:
            rev_counts = Counter(scalar(x.get("revision_status")) for x in projects)
            lines.append("- Revisión de proyectos (indicadores independientes): " + ", ".join(f"{s} {rev_counts[s]}" for s in ("PENDING", "APPROVED", "REJECTED")))
            other = sum(n for s, n in rev_counts.items() if s not in REVIEW_STATUSES)
            if other:
                lines.append(f"- Proyectos con estado de revisión ausente/desconocido: {other}")
    pending, done, _ = known_count(tasks)
    unknown_items = [x for x in tasks if x.get("task_status") not in KNOWN_STATUSES]
    lines.append(f"\n### Total global" + (" (parcial)" if not complete else ""))
    lines.append(f"- PENDING {pending}, DONE {done}; entregadas {pct(done, pending)}; estados ausentes/desconocidos {len(unknown_items)}")
    projects = [x for x in tasks if task_type(x) == "PROJECT"]
    if projects:
        rev_counts = Counter(scalar(x.get("revision_status")) for x in projects)
        lines.append("- Revisión de proyectos (independiente del porcentaje): " + ", ".join(f"{s} {rev_counts[s]}" for s in ("PENDING", "APPROVED", "REJECTED")))
    return lines


def activity_type(event: dict[str, Any]) -> str | None:
    for key in ("activity_type", "type", "event_type", "slug", "name"):
        found = scalar(event.get(key))
        if found:
            return found
    return None


def render_activity() -> list[str]:
    return ["\n## Actividad registrada", "No disponible: la API denegó el acceso a la actividad (HTTP 403). No se muestran recuentos; la actividad no se puede inferir de las tareas y no representa un porcentaje de avance académico."]
    events = payload if isinstance(payload, list) else payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(events, list):
        lines.append("Formato de actividad no reconocido; no se muestran recuentos.")
        return lines
    counts: Counter[tuple[str, str]] = Counter()
    unknown_type = 0
    for event in events:
        if not isinstance(event, dict):
            continue
        kind = activity_type(event)
        if not kind:
            unknown_type += 1
            continue
        counts[(cohort_key(event) or "Cohorte no disponible", kind)] += 1
    if not counts and not unknown_type:
        lines.append("No hay eventos devueltos.")
    for (cohort, kind), count in sorted(counts.items()):
        lines.append(f"- {cohort} — {kind}: {count}")
    if unknown_type:
        lines.append(f"- Tipo de actividad no disponible: {unknown_type}")
    return lines


def main() -> int:
    tasks, complete, task_error = get_tasks()
    lines = render_tasks(tasks, complete, task_error)
    lines.extend(render_activity())
    print("\n".join(lines))
    return 1 if task_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
