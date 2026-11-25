---
name: consultar-feedback-proyectos
description: Consulta los comentarios y resultados de corrección docente de los proyectos propios asignados en 4Geeks; no usar para revisiones de código de Rigobot ni feedback de encuestas.
---

# Consultar feedback de mis proyectos

## Ejecución

1. Lee las instrucciones de `fourgeeks-api-common`. Usa únicamente el cliente común para consultas GET; no accedas directamente a credenciales, no uses rutas de academia ni de Rigobot y no realices escrituras.
2. Recupera todas las páginas de `GET /v1/assignment/user/me/task` filtrando `task_type=PROJECT`, con `limit` y `offset`. Procesa las respuestas en memoria. Conserva el orden recibido y deduplica únicamente si la paginación repite el mismo ID.
3. Para cada ID numérico de proyecto recuperado, consulta `GET /v1/assignment/task/{task_id}` mediante la capa común. Esta ruta de detalle ya está permitida. No uses IDs aportados por fuentes externas al listado personal.
4. Presenta solo proyectos con estado de revisión explícito `APPROVED` o `REJECTED`, o con `reviewed_at` presente. Si la tarea parece revisada pero falta un campo, muestra el estado literal disponible y marca el resto como no disponible; no infieras una corrección a partir del título, fecha u otro campo.
5. Por proyecto muestra título, estado (`task_status` y `revision_status`), comentario textual de corrección (`description`) y fecha (`reviewed_at`) solo si existen. La consulta verificada mostró `description` con el comentario «Buen trabajo.» para un proyecto aprobado; trátalo como texto de feedback docente, no como descripción original. No lo reformules de forma que cambie su sentido.
6. No hay evidencia de un campo numérico independiente de puntuación ni de campos separados de recomendaciones u observaciones. No los inventes: indícalos como «no disponibles en los campos consultados» si la usuaria los solicita. `description` puede contener comentarios textuales, pero no presupongas que siempre incluya una justificación extensa.
7. Si no hay proyectos revisados en el conjunto completo, dilo solo después de confirmar que todas las páginas se recuperaron correctamente. Si falla una página, marca el resultado como incompleto y no concluyas que no existen más. Si falla el detalle de un proyecto, reporta ese fallo de forma segura y continúa con los demás.
8. No expongas IDs, datos del campo `user`, emails, cohortes, URLs de repositorios, telemetría, JSON bruto ni cuerpos de error salvo que la usuaria los pida expresamente y sean necesarios. El cliente puede habilitar `FOURGEEKS_API_OUTPUT_JSON=1` solo en el proceso hijo confiable; captura stdout directamente en memoria, selecciona campos permitidos y jamás lo imprimas ni lo persistas.

## Campos confirmados

El serializador de detalle de tareas devuelve, entre otros, `title`, `task_status`, `description`, `revision_status`, `reviewed_at`, `delivered_at`, `opened_at`, `read_at`, `created_at`, `updated_at`, `task_type`, `cohort`, `user` y `assignment_telemetry`. Para esta skill solo hacen falta título, estados, comentario y fecha de revisión. No muestres los campos personales ni telemetría.

## Consulta

Usa `GET /v1/assignment/user/me/task` y `GET /v1/assignment/task/{task_id}` exclusivamente a través de `/root/.openclaw/workspace/skills/fourgeeks-api-common/scripts/run_api_get.py`. Las dos formas están ya en la allowlist común; no la amplíes para esta skill.
