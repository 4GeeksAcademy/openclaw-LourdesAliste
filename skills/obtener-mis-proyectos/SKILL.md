---
name: obtener-mis-proyectos
description: Recupera los proyectos asignados de 4Geeks y presenta su estado, cohorte, fechas y datos de revisión disponibles.
---

# Obtener mis proyectos

## Ejecución

1. Lee las instrucciones de `fourgeeks-api-common` antes de consultar la API. No leas el archivo de credenciales ni implementes autenticación aquí.
2. Consulta todas las tareas del usuario con `GET /v1/assignment/user/me/task`, usando `task_type=PROJECT`, sin filtrar por estado. La vista del API aplica paginación si se pasa `limit` u `offset`; el sobre contiene `count`, `first`, `next`, `previous`, `last` y `results`. Recorre mediante `limit`/`offset` hasta que `next` sea nulo (o el offset alcance `count`), conservando el orden recibido. Sin parámetros de paginación la vista puede devolver lista plana; por ello, siempre envía ambos parámetros.
3. En caso de error inicial, informa «No se han podido recuperar los proyectos» y el código HTTP o tipo de fallo disponible. No muestres secciones vacías ni afirmes que no existen proyectos.
4. Por cada proyecto recuperado, consulta `GET /v1/assignment/task/{task_id}`. Si falla, conserva los campos disponibles del listado, incluye «No se pudo obtener el detalle de este proyecto» y el HTTP/status o tipo de error seguro. No expongas cuerpo de error.
5. Clasifica usando ambos campos explícitos, sin deducir estado: `task_status=PENDING` → Pendientes; `task_status=DONE` → Entregados solo si `revision_status` no es `APPROVED`/`REJECTED`; cuando `revision_status=APPROVED` o `REJECTED`, clasifica en Calificados y distingue Aprobados/Rechazados. Si `task_status` mismo fuera `APPROVED` o `REJECTED`, también clasifica bajo Calificados. Para estado desconocido/ausente, usa exactamente «Estado no identificado: [valor literal]» o «Estado no identificado: sin valor». No confundas `revision_status=PENDING` con `task_status=PENDING`: si `task_status=DONE` y revisión pendiente, está Entregado. Si combinación entra en conflicto o falta el dato requerido para resolverla, reporta el literal y no inventes categoría.
6. Mantén este orden de secciones: Pendientes; Entregados; Calificados (Aprobados y Rechazados). Conserva el orden recibido de la API dentro de cada agrupación. Incluye todas las secciones incluso vacías; solo después de confirmar que el listado completo terminó correctamente, usa «No hay proyectos en este estado» para las vacías.
7. Por proyecto muestra solo datos relevantes realmente presentes en las respuestas: título, cohorte, fechas disponibles, estado(s) literales, puntuación/feedback u otra información explícita de revisión, enlaces de entrega y descripción breve si procede. El serializador listado aquí documenta `id`, `title`, `task_status`, `associated_slug`, `description`, `revision_status`, `github_url`, `live_url`, `task_type`, `opened_at`, `read_at`, `reviewed_at`, `delivered_at`, `cohort` (`id`, `name`, `slug`), `created_at` y `updated_at`. El serializador de detalle añade `user` y `assignment_telemetry`. La API no documenta un campo directo de puntuación/comentarios en estos serializadores; si no aparece en la respuesta, indícalo como no disponible, sin presentarlo como feedback.
8. Si falla una página posterior, incluye las tareas ya recuperadas y advierte claramente que la lista es incompleta, con el HTTP/status o tipo de fallo seguro. No afirmes que los grupos estén vacíos en el conjunto completo.
9. No imprimas el JSON bruto ni lo escribas a ficheros. El JSON solo se procesa en memoria. No muestres datos personales del campo `user` ni telemetry. No realices operaciones de escritura en la API.

## Consultas mediante capa común

Ejecuta `python3 /root/.openclaw/workspace/skills/obtener-mis-proyectos/scripts/show_projects.py`. El programa hace las consultas solo mediante `run_api_get.py`, habilita `FOURGEEKS_API_OUTPUT_JSON=1` solo en el proceso hijo, captura stdout en memoria y no persiste ni registra cuerpos. No invoques el modo JSON desde una terminal interactiva.

## Verificación

Ejecuta las pruebas offline con `python3 -m unittest discover -s /root/.openclaw/workspace/skills/obtener-mis-proyectos/tests -v`, además de las pruebas de `fourgeeks-api-common`; valida la skill con `python /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/quick_validate.py /root/.openclaw/workspace/skills/obtener-mis-proyectos`.
