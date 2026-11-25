---
name: obtener-trabajo-pendiente
description: Identifica y resume las tareas asignadas pendientes de 4Geeks (proyectos, ejercicios y lecciones), con detalles solo para las pendientes.
---

# Obtener trabajo pendiente

## Ejecución

1. Lee las instrucciones de `fourgeeks-api-common`. Realiza exclusivamente consultas GET a través de su `run_api_get.py`; nunca gestiones credenciales directamente ni hagas operaciones de escritura.
2. Recupera todas las páginas de `GET /v1/assignment/user/me/task`, sin filtro `task_status` ni filtro de cohorte. Pasa `task_type=PROJECT,EXERCISE,LESSON`, `limit` y `offset`. Conserva el orden recibido de cada página. No anuncies que no hay pendientes si la recuperación falla, la paginación no se puede verificar o queda incompleta.
3. Clasifica después de recuperar cada resultado: `task_status` exactamente `PENDING` = pendiente; `DONE` no se muestra. Según el modelo API actual, `task_status` solo define `PENDING` y `DONE`; cualquier otro valor, incluidos `APPROVED`/`REJECTED`, y estados ausentes van en «Estado no identificar», presentando el literal tal como llegó o «Sin estado» si falta. No uses `revision_status` para clasificar ni muestres tareas `DONE`.
4. Para cada pendiente, solicita `GET /v1/assignment/task/{id}`. No solicites detalles para estados desconocidos/ausentes ni para otras tareas. Si falta un ID válido o falla el detalle, conserva la entrada del listado y añade exactamente «No se pudo obtener el detalle de esta tarea» junto con el error seguro disponible, cuando exista.
5. Construye la respuesta sin inferir requisitos. Incluye primero «Resumen de tareas pendientes», con cada título —si falta, «no identificada»— e ID cuando exista, tipo y cohorte cuando la API los proporcione. Sigue con «Detalle de tareas pendientes», en el mismo orden, con instrucciones solo si existen, descripción, fechas, tipo, cohorte y otros campos del listado/detalle útiles para comprender la tarea. Si los datos disponibles no aclaran qué falta por hacer, dilo expresamente. Representa los campos relevantes ausentes como «no disponible». Después muestra «Estado no identificar» con los datos disponibles del listado y el estado literal, o «Sin estado».
6. Si el listado completo terminó correctamente y no hay tareas `PENDING`, indica «No tienes tareas pendientes». Si falla una página posterior, conserva lo recuperado y advierte que el resultado está incompleto; nunca afirmes que no hay pendientes en ese caso. Un fallo inicial se comunica como imposibilidad de recuperar el listado, con error seguro cuando exista.
7. No muestres JSON bruto, campos personales de `user` ni `assignment_telemetry`; no persistas respuestas API ni registres cuerpos. El detalle del API no garantiza un campo estructurado de instrucciones o pasos restantes: expón lo devuelto y señala explícitamente la insuficiencia de información cuando corresponda.

## Implementación

Ejecuta `python3 /root/.openclaw/workspace/skills/obtener-trabajo-pendiente/scripts/show_pending_work.py`. El helper captura la salida JSON del cliente común en memoria únicamente y presenta campos seleccionados.

## Verificación

Ejecuta `python3 -m unittest discover -s /root/.openclaw/workspace/skills/obtener-trabajo-pendiente/tests -v` y valida con `python /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/quick_validate.py /root/.openclaw/workspace/skills/obtener-trabajo-pendiente`.
