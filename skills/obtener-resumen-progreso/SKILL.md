---
name: obtener-resumen-progreso
description: Resume el progreso de tareas asignadas y la actividad registrada de 4Geeks, separado por cohorte y tipo, sin confundir actividad con avance académico.
---

# Obtener resumen del progreso

## Ejecución

1. Lee las instrucciones de `fourgeeks-api-common`. Usa exclusivamente consultas GET mediante `run_api_get.py`; procesa JSON en memoria y no persistas respuestas ni imprimas campos personales, `user` o `assignment_telemetry`.
2. Recupera todas las páginas de `GET /v1/assignment/user/me/task`, sin filtro de estado ni cohorte, usando `task_type=PROJECT,EXERCISE,LESSON,QUIZ`, `limit` y `offset`. Conserva estados y tipos literales. Si la paginación falla o no puede verificarse, marca los recuentos como parciales; nunca presentes una recuperación incompleta como total.
3. No llames a `GET /v1/admissions/academy/cohort/me`: actualmente responde HTTP 403. Presenta solo las cohortes que estén explícitamente identificadas en los registros de tareas, sin atribuir por inferencia. Aclara que no se enumeran cohortes sin tareas y que esta vista no garantiza una lista completa. Tareas sin cohorte identificable se agrupan en «Cohorte no disponible».
4. En **Progreso de tareas**, presenta por cohorte y tipo independiente (`PROJECT`, `EXERCISE`, `LESSON`, `QUIZ`, además de cualquier tipo literal desconocido): recuentos `task_status=PENDING` y `DONE`, y porcentaje `DONE / (PENDING + DONE)` por tipo y total de cohorte cuando el denominador sea mayor que cero. Si el denominador es cero, escribe «Avance no disponible». Estados ausentes o desconocidos se muestran en una lista separada con datos identificativos mínimos y no entran en porcentajes. Tareas sin cohorte van en su apartado separado y pueden formar parte de los totales globales, pero nunca de porcentajes individuales de cohortes.
5. Los proyectos se consideran solamente los elementos con `task_type=PROJECT`. Presenta recuentos independientes de `revision_status=PENDING`, `APPROVED` y `REJECTED`; no los sumes al denominador ni los uses para cambiar el porcentaje de tareas entregadas. Incluye estado de revisión ausente/desconocido aparte, si existe. No presentes como trabajos calificados tareas de otros tipos.
6. Calcula el total global con recuentos sumados, incluidos los elementos sin cohorte. Si incluyes porcentaje global, calcula `DONE / (PENDING + DONE)` sobre los estados identificables, no promedies porcentajes de cohortes y aclara que es un cálculo sobre tareas asignadas, no una métrica oficial de finalización del curso. Las calificaciones siguen siendo indicadores independientes.
7. No llames a `GET /v1/activity/me`: actualmente responde HTTP 403. En **Actividad registrada**, indica que el acceso fue denegado y que no hay recuentos disponibles. No estimes eventos ni los infieras desde tareas. Mantén esta sección separada y aclara que la actividad no representa porcentaje académico.
8. Si falla el listado de tareas, comunica la sección no recuperable y conserva los datos parciales identificando su carácter incompleto. No muestres cuerpos JSON brutos ni errores que expongan información sensible.

## Implementación

Ejecuta `python3 /root/.openclaw/workspace/skills/obtener-resumen-progreso/scripts/show_progress.py`. El helper usa la capa común, captura JSON solo en memoria y presenta campos agregados seleccionados.

## Verificación

Ejecuta `python3 -m unittest discover -s /root/.openclaw/workspace/skills/obtener-resumen-progreso/tests -v` y valida con `python3 /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/quick_validate.py /root/.openclaw/workspace/skills/obtener-resumen-progreso`.
