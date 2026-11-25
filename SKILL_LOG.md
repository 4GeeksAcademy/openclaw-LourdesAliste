# Bitácora histórica: integración de C3PO con la API de 4Geeks

**Fecha de trabajo documentada:** 24 de noviembre de 2026 (UTC).  
**Alcance:** conexión autenticada de solo lectura, creación de `fourgeeks-api-common` y diseño, implementación y verificación de «Obtener mis proyectos».  
**Estado final:** primera skill implementada y verificada, pendiente de revisión de Lourdes antes de iniciar otra skill.

> **Alcance histórico y límites de recuperación.** Este documento reúne los mensajes literales que se pudieron recuperar del historial visible y los resultados técnicos registrados. El historial disponible no ofrece todos los turnos antiguos en forma íntegra: parte fue compactada y parte de las páginas de transcript se entrega truncada. Por tanto, no afirmo que la conversación reproducida sea una transcripción total. Cada laguna se señala; no se reconstruyen mensajes ausentes ni se presentan resúmenes como citas. Se omiten cuerpos de respuestas API y datos personales. En cualquier reproducción de credenciales o secretos se usaría `[*********]`; aquí no se registra ningún valor secreto.

---

# Bloque 1. Conexión de C3PO con la API de 4Geeks

## 1.1 Resumen del trabajo

**Objetivo.** Permitir que C3PO realice consultas autenticadas, de solo lectura, a 4Geeks para apoyar skills de aprendizaje. La primera aplicación fue obtener proyectos asignados.

**Configuración.** `TOKEN_4GEEKS` se lee de `/root/.openclaw/.env` (el valor queda protegido y no se reproduce). El lanzador lee la asignación sin ejecutar el archivo como shell; valida que sea un archivo regular, propiedad del usuario del proceso y sin permisos de grupo/otros, y pasa el valor únicamente al entorno del proceso hijo. La petición usa `Authorization: Token [*********]`. El `.env` no se modificó y no se creó una copia persistente del token.

**Reglas de conexión.** Base URL `https://breathecode.herokuapp.com`; solo método GET y rutas explícitamente permitidas; TLS validado; redirecciones bloqueadas; parámetros URL-encoded; límite de respuesta de 2 MB; JSON validado. Los cuerpos exitosos y de error se suprimen por defecto. Para procesamiento interno de confianza se habilita `FOURGEEKS_API_OUTPUT_JSON=1` solo en el proceso hijo y se captura el contenido en memoria, sin imprimirlo, registrarlo ni persistirlo.

**Endpoints usados por la primera skill.** `GET /v1/assignment/user/me/task` (`task_type=PROJECT`, `limit=100`, `offset` paginado) y `GET /v1/assignment/task/{task_id}`.

**Endpoints presentes en el allowlist común documentado.** `/v1/admissions/user/me`, `/v1/admissions/academy/cohort/me`, `/v1/assignment/user/me/task`, `/v1/assignment/task/{task_id}` (ID numérico), `/v1/activity/me`, `/v1/registry/asset`, `/v1/registry/asset/me`, `/v1/registry/asset/{asset_slug}` (un segmento permitido), `/v1/registry/technology` y `/v1/events/all`. El allowlist no autoriza escrituras; que una ruta esté admitida no significa que cualquier skill deba consultarla.

**Resultado y estado.** Una consulta real `GET /v1/admissions/user/me` fue aceptada durante la verificación de la capa común y su cuerpo quedó suprimido. La capa común quedó operativa para la skill desarrollada. Cuatro skills existentes no se integraron en esa fase.

## 1.2 Conversación recuperable

### Límite de esta sección

La conversación inicial que dio origen a la conexión y todos sus mensajes no está íntegra en las páginas del historial consultables ahora. En particular, no se pudo recuperar una transcripción literal completa del diseño inicial de autenticación, de las propuestas intermedias de seguridad ni de los comandos y salidas de cada paso de creación de la capa común. Los datos técnicos de arriba proceden del registro técnico conservado, no son citas conversacionales.

### Mensajes literales disponibles, en orden temporal

**Lourdes:** «En que punto nos quedamos?»

**C3PO:** «Nos quedamos con la **capa común de consulta 4Geeks** implementada y verificada:

- El lanzador `run_api_get.py` lee `TOKEN_4GEEKS` del `.env` original, sin modificarlo ni crear una copia persistente, y lo pasa al cliente solo durante la ejecución.
- El cliente permite únicamente consultas `GET` a rutas autorizadas, valida TLS, bloquea redirecciones y no muestra el contenido de las respuestas.
- Las **seis pruebas offline pasaron**. Después, una consulta real `GET /v1/admissions/user/me` fue aceptada; el cuerpo se suprimió.
- Las cuatro skills aún **no están integradas**. Ese sería el siguiente paso, empezando por revisarlas y definir qué rutas necesita cada una.»

**Lourdes:** «Perfecto. Damos por completada y verificada la capa común de autenticación y consulta de 4Geeks.
Vamos a implementar las 4 skills. Lo haremos una a una. 
La primera skill tendra como titulo **Obtener mis proyectos**, y su objetivo será recuperar la lista de proyectos que tengo asignados con su estado actual (pendiente, entregado y calificado)
Para ello:
- Investiga en la documentación de la API qué endpoint permite obtener \"mis proyectos\", qué parámetros necesita y qué información devuelve.
- Explícame cómo podemos identificar los tres estados y si la API proporciona los campos necesarios.
- Propón la estructura básica de la skill, los archivos necesarios y las pruebas que deberíamos realizar.
- Guíame mediante preguntas sencillas, de una en una, para decidir cómo va a funcionar.
No modifiques ni crees archivos todavía. Primero quiero definir contigo la estructura y el funcionamiento de la skill. 
No avances a la segunda skill hasta que hayamos terminado y validado ésta.»

Este mensaje marca la transición: la capa común se dio por completada y la siguiente fase debía centrarse solo en la primera skill, sin crear archivos antes de acordar su diseño.

---

# Bloque 2. Creación de la capa común `fourgeeks-api-common`

## 2.1 Resumen del trabajo

**Objetivo y motivo.** Centralizar en un solo cliente los controles de autenticación y seguridad de lectura, evitando que cada skill gestione credenciales y peticiones de forma distinta.

**Archivos y función.**

- `skills/fourgeeks-api-common/SKILL.md`: instrucciones de invocación, seguridad, límites y verificaciones.
- `skills/fourgeeks-api-common/README.md`: descripción breve del cliente y referencia a sus instrucciones.
- `skills/fourgeeks-api-common/docs/ROUTES.md`: base URL, rutas permitidas y advertencias del modo JSON interno.
- `skills/fourgeeks-api-common/scripts/run_api_get.py`: lectura controlada de la variable de entorno desde el archivo privado y lanzamiento del cliente.
- `skills/fourgeeks-api-common/scripts/api_get.py`: cliente HTTP exclusivamente GET, allowlist, validación TLS/JSON, bloqueo de redirecciones, límite de tamaño y supresión de cuerpos por defecto.
- `skills/fourgeeks-api-common/tests/test_api_get.py`: pruebas sin red para allowlist, token ficticio, petición GET, supresión y opt-in JSON, y bloqueo de redirecciones.

**Pruebas y resultados registrados.** Las pruebas offline pasaron: inicialmente se registraron 6; tras ampliar cobertura, la bitácora final registra 7. También pasaron `py_compile` y `git diff --check`. Una consulta live `GET /v1/admissions/user/me` se aceptó sin mostrar su cuerpo. Las pruebas usaron fixture/token ficticio, no la credencial real.

**Evolución técnica relevante.** El modo original suprimía por completo los cuerpos, lo que impedía que el programa de la skill clasificara proyectos. Se añadió `FOURGEEKS_API_OUTPUT_JSON=1` como opt-in explícito para procesamiento interno confiable. No se habilita de manera interactiva; el programa captura stdout en memoria y no registra ni almacena la respuesta.

## 2.2 Conversación recuperable

La autorización literal disponible cubre la implementación de la skill y el análisis acordado; no se ha encontrado un mensaje separado que diga literalmente «autorizo crear la capa común». El historial técnico indica que la adaptación era necesaria para que la skill pudiera procesar respuestas estructuradas. No convierto esa necesidad técnica en una cita o autorización independiente.

**C3PO (respuesta anterior a la aprobación de la skill):** «Hay un bloqueo técnico que conviene resolver antes de diseñar la implementación: el cliente común actual **suprime los cuerpos de respuesta**, por lo que la skill no puede leer proyectos ni detalles para mostrarlos. ¿Te parece bien que, cuando aprobemos el diseño, ajustemos la capa común para que el flujo interno pueda procesar JSON de forma controlada, sin imprimirlo en logs ni en la salida visible?»

**Lourdes:** «Sí, estoy de acuerdo.»

**C3PO:** «Entendido. Queda aprobado **ajustar más adelante la capa común** para que la skill pueda procesar las respuestas sin escribirlas a disco ni mostrar el JSON bruto en logs o en la salida visible. Mantendremos la consulta de solo lectura y el control de rutas. No haré cambios todavía.

La propuesta conserva lo acordado: listar todos los proyectos mediante paginación, consultar cada detalle, agruparlos en el orden establecido, y mostrar solo los datos relevantes que devuelva la API —incluida cohorte y fechas cuando existan—, sin completar los ausentes.

Para cerrar la presentación: **¿en qué orden prefieres los proyectos dentro de cada grupo: alfabético por nombre o el orden en que los devuelve la API?**»

**Lourdes:** «En el orden que los devuelve el API».

**C3PO:** «Perfecto: dentro de cada grupo conservaré el orden en que la API devuelve los proyectos.

Para cerrar cómo manejar errores parciales: **si falla la consulta del detalle de un proyecto, ¿quieres que lo incluya igualmente con los datos del listado y una nota de que no se pudo obtener el detalle?**»

El historial disponible no conserva aquí todos los mensajes intermedios de implementación de la capa común, ni todos sus comandos y resultados en forma de conversación. Los componentes, restricciones y resultados se registran en el resumen técnico de la sección 2.1. No se inventa un diálogo para cubrir esa laguna.

---

# Bloque 3. Diseño, implementación y verificación de «Obtener mis proyectos»

## 3.1 Resumen del trabajo

**Objetivo.** Recuperar todos los proyectos asignados y presentarlos por estado, con los datos disponibles pertinentes, sin inventar campos o valores ni mostrar datos personales.

**Diseño y decisiones.**

- Consultar listado con `GET /v1/assignment/user/me/task`, `task_type=PROJECT`, `limit=100` y `offset` sucesivos; no filtrar por estado y mantener orden de API.
- Consultar `GET /v1/assignment/task/{task_id}` para cada proyecto.
- Agrupar como **Pendientes**, **Entregados** y **Calificados**, separando **Aprobados** y **Rechazados**.
- Diferenciar `task_status` de `revision_status`: `PENDING` de tarea no equivale a `PENDING` de revisión. Estados ausentes o no reconocidos se muestran literalmente como «Estado no identificado: …» o «Estado no identificado: sin valor».
- Mostrar los grupos vacíos solo tras completar correctamente el listado. Un fallo inicial no es una lista vacía; un fallo de página conserva los resultados y advierte que son parciales.
- Si falla el detalle, conservar el proyecto y toda la información disponible del listado, añadir «No se pudo obtener el detalle de este proyecto» e indicar el error/tipo y lo que no se pudo recuperar, sin cuerpo bruto.
- Mostrar cohorte, fechas y demás datos pertinentes solo cuando estén presentes. No afirmar que hay puntuación si no se ha verificado; excluir `user` y `assignment_telemetry`.

**Archivos.** `skills/obtener-mis-proyectos/SKILL.md` define el contrato de uso y presentación; `scripts/show_projects.py` consulta páginas/detalles, clasifica y renderiza; `tests/test_show_projects.py` prueba paginación/orden, clasificación, grupos vacíos y errores.

**Verificación.** Se registraron 6 pruebas offline de la skill y 7 del cliente común correctas; `quick_validate.py`, `py_compile` y `git diff --check` correctos. La consulta real GET completó listado paginado y detalles sin fallos reportados. Resultado documentado: 6 pendientes, 1 entregado, 15 aprobados, 0 rechazados. No se documentó puntuación ni se copiaron títulos, comentarios o datos personales.

**Estado.** Primera skill implementada y probada, pendiente de revisión de Lourdes. No se inició la segunda skill.

## 3.2 Conversación completa recuperable

Los mensajes y respuestas siguientes se reproducen literalmente cuando el historial disponible los conserva. Las herramientas y sus salidas se condensan solo cuando incluyen datos privados o cuerpos API; se especifica la acción y el resultado sin copiar esos datos. La cadena de mensajes completa desde el primer análisis no pudo recuperarse íntegramente; la laguna se describe al final de este bloque.

### Inicio y alcance

**Lourdes:** «Perfecto. Damos por completada y verificada la capa común de autenticación y consulta de 4Geeks.
Vamos a implementar las 4 skills. Lo haremos una a una. 
La primera skill tendra como titulo **Obtener mis proyectos**, y su objetivo será recuperar la lista de proyectos que tengo asignados con su estado actual (pendiente, entregado y calificado)
Para ello:
- Investiga en la documentación de la API qué endpoint permite obtener \"mis proyectos\", qué parámetros necesita y qué información devuelve.
- Explícame cómo podemos identificar los tres estados y si la API proporciona los campos necesarios.
- Propón la estructura básica de la skill, los archivos necesarios y las pruebas que deberíamos realizar.
- Guíame mediante preguntas sencillas, de una en una, para decidir cómo va a funcionar.
No modifiques ni crees archivos todavía. Primero quiero definir contigo la estructura y el funcionamiento de la skill. 
No avances a la segunda skill hasta que hayamos terminado y validado ésta.»

**C3PO:** «La referencia local de la API apunta a este endpoint para consultar las tareas asignadas:

`GET /v1/assignment/user/me/task`

Admite filtros útiles como `task_type=PROJECT`, `task_status` (`PENDING`, `DONE`, `APPROVED`, `REJECTED`), `cohort`, y paginación con `limit` y `offset`. Para esta skill, lo más directo sería pedir las tareas de tipo `PROJECT` y revisar el estado de cada una.

**Cómo interpretar los estados:** `PENDING` corresponde a pendiente; `DONE`, a completada o entregada por ti; `APPROVED` y `REJECTED` indican que hubo revisión. Pero la referencia no confirma si la respuesta incluye un campo separado de calificación o una fecha de entrega. Así que todavía no podemos asegurar que esos datos permitan distinguir exactamente «entregado» de «calificado» sin revisar el esquema OpenAPI y los campos reales documentados. La respuesta está descrita como una lista con estados, fechas y metadatos de revisión.

**Estructura inicial propuesta:** una carpeta de skill con `SKILL.md` para explicar cuándo y cómo consultar el endpoint, usando la capa común de solo lectura; no hace falta duplicar autenticación ni crear un script auxiliar de entrada. Si la skill necesita transformar estados o probar esa clasificación con lógica propia, podríamos añadir un pequeño helper y sus pruebas. De momento, no modificaré ni crearé archivos.

Primero necesito cerrar una decisión de alcance: **¿quieres que la skill muestre solo los proyectos pendientes, entregados y calificados, o todos los proyectos asignados, incluidos los rechazados?**»

**Lourdes:** «Quiero que muestre todos los proyectos, incluidos los rechazados.
Mantén los tres estados principales que definimos: pendiente, entregado y calificado. 
Sin embargo, investiga qué campos ofrece realmente la respuesta para poder definir correctamente la clasificación. 
No inventes estados ni deduzcas resultados. Comprueba si existe la opcion de que haya comentarios.»

**C3PO (respuesta conservada):** explicó que la documentación local y Swagger no permitían confirmar los nombres exactos de los campos; el endpoint de listado documentaba filtros, estados y paginación, mientras que el detalle podía incluir descripción, puntuación y feedback sin especificar nombres ni presencia garantizada. Señaló que la skill no debía inferir comentarios/puntuación. Propuso consultar todas las páginas y cada detalle, conservar el orden, mantener estados no identificados explícitos, y pidió autorización para adaptar el cliente común porque suprimía los cuerpos. Esta respuesta completa quedó conservada en la etapa anterior del historial, pero no todas las respuestas iniciales aparecen en la captura íntegra; el resumen se marca como tal.

### Orden, fallo de detalle y fallo de páginas

**Lourdes:** «En el orden que los devuelve el API».

**C3PO:** «Perfecto: dentro de cada grupo conservaré el orden en que la API devuelve los proyectos.

Para cerrar cómo manejar errores parciales: **si falla la consulta del detalle de un proyecto, ¿quieres que lo incluya igualmente con los datos del listado y una nota de que no se pudo obtener el detalle?**»

**Lourdes:** «Sí, incluye toda la información disponible en el listado y añade una nota: «No se pudo obtener el detalle de este proyecto».
No omitas el proyecto ni inventes los datos que falten. 
Mantén visible el error porsi se puede identificar qué información no se ha podido recuperar.»

**C3PO:** «Entendido. Si falla el detalle, conservaré el proyecto con todos los datos disponibles del listado y añadiré: **«No se pudo obtener el detalle de este proyecto»**. También indicaré el error identificable y qué información del detalle no se pudo recuperar; no mostraré cuerpos de respuesta que puedan contener datos personales.

Una decisión para concretarlo: **¿te parece bien que el error visible incluya el código HTTP o tipo de fallo y el nombre de los datos que no se pudieron recuperar, pero no el cuerpo bruto de la respuesta?**»

**Lourdes:** «perfecto».

**C3PO:** «Perfecto. El error visible incluirá el código HTTP o tipo de fallo y señalará qué información del detalle no se pudo recuperar, sin exponer el cuerpo bruto de la respuesta.

También queda definido que los proyectos mantienen el orden de la API y, si falla un detalle, no se omite el proyecto: se muestra lo disponible del listado con la nota acordada.

Una última decisión sobre fallos parciales: **si falla una página del listado, ¿quieres que muestre los proyectos ya recuperados y avise claramente que la lista está incompleta?**»

**Lourdes:** «si».

**C3PO:** «Anotado: si falla una página de resultados, mostraré los proyectos recuperados hasta ese punto, conservaré el orden de la API y señalaré claramente que la lista está incompleta, junto con el código HTTP o tipo de fallo disponible. No presentaré esa lista parcial como completa. **Si falla la primera consulta del listado y no se recupera ningún proyecto, ¿quieres que la skill muestre un mensaje de error en lugar de “No hay proyectos en este estado”?**»

**Lourdes:** «Si falla la consulta inicial del listado, muestra un mensaje de error indicando que no se han podido recuperar los proyectos. No muestres «No hay proyectos en este estado», porque no podemos confirmar que la lista esté vacía.
Reserva ese mensaje únicamente para cuando la consulta se complete correctamente y no haya proyectos en ese estado.»

**C3PO:** «Queda definido: si falla la consulta inicial, la skill indicará que no pudo recuperar los proyectos y mostrará el error disponible. **«No hay proyectos en este estado»** aparecerá solo si la consulta del listado se completa correctamente y ese grupo está vacío.»

### Estados y grupos vacíos

**Lourdes:** «Que aparezcan agrupados por estado principal, en el siguiente orden:
1_ Pendientes
2_ Entregados
3_ Calificados, distinguiendo entre aprobados y rechazados.
Por proyecto muesta la información disponible»

**C3PO:** «De acuerdo. La salida quedaría agrupada en este orden:

1. **Pendientes** — tareas cuyo estado de la API sea `PENDING`.
2. **Entregados** — tareas cuyo estado sea `DONE`.
3. **Calificados**
   - **Aprobados** — `APPROVED`.
   - **Rechazados** — `REJECTED`.

Dentro de cada proyecto, mostraríamos **los campos que realmente devuelvan el listado y su detalle**, incluidos puntuación, comentarios o información de revisión solo cuando estén presentes. No rellenaríamos datos ausentes ni traduciríamos un estado desconocido a una categoría inventada; lo señalaríamos como no disponible o mostraríamos el valor original, según corresponda.

Aún no pude comprobar el esquema exacto en OpenAPI: la referencia local enumera esos estados y menciona feedback en el detalle, pero no concreta los nombres de los campos; además, la consulta de Swagger no fue accesible desde el navegador disponible. Lo dejo como una verificación pendiente antes de implementar.

Una decisión para cerrar esa salida: **si una tarea llega sin estado o con uno distinto de esos cuatro, ¿quieres que vaya en una sección aparte llamada “Estado no identificado”?**»

**Lourdes:** «No. Si la API devuelve un estado distinto de los cuatro identificados, quiero que ponga: “Estado no identificado” seguido del valor literal que devuelva la API, sin interprecion.
Si la API no devuelve ningún estado, indica “Estado no identificado: sin valor”.»

**C3PO:** «Entendido. Si el estado es otro, mostraré **“Estado no identificado: [valor literal]”**, sin interpretarlo. Si la API no devuelve un estado, mostraré **“Estado no identificado: sin valor”**.

Una decisión de presentación: **¿quieres que aparezcan también los grupos vacíos (por ejemplo, “Pendientes” aunque no haya ninguno)?**»

**Lourdes:** «Sí, que eso anima. Quiero que aparezcan todos los grupos, aunque estén vacíos. En ese caso, muestra el mensaje “No hay proyectos en este estado”.»

**C3PO:** «Anotado: mostraré **todos los grupos**, incluso los vacíos, con el mensaje “No hay proyectos en este estado”. Para los estados no identificados usaré el formato literal acordado, sin crear una categoría ni interpretar su significado.

Sigue pendiente confirmar los campos exactos que ofrece el listado y el detalle; la documentación local no los especifica y Swagger no fue accesible desde el navegador disponible. Mientras verificamos eso, una decisión de presentación: **si la API proporciona cohorte o fechas, ¿quieres que también aparezcan junto a cada proyecto?**»

### Investigación de campos, propuesta consolidada y aprobación

**Lourdes:** «Sí, muestra también la cohorte y las fechas disponibles junto a cada proyecto. 
Incluye únicamente los datos que devuelva la API y que sean relevantes, sin inventar ni completar información ausente.
Con respecto a la decision pendiente, investiga los campos exactos que devuelven los dos endpoints:
- GET /v1/assignment/user/me/task
- GET /v1/assignment/task/{task_id}
Busca la informaciónque necesitas. No muestres datos personales ni modifiques información.
Si algun campo no se puede verifiar, indicalo.
Cuando termines, presenta la actualización de la propuesta de estructura y funcionamiento de la skill.»

**C3PO (respuesta conservada):** informó que el Swagger cargaba pero no se pudo recuperar su especificación; la documentación confirmaba filtros y tipos generales, pero no todos los nombres de campos. No se consultaron ni mostraron datos personales. La propuesta mantenía listado paginado, detalle por proyecto, agrupaciones, estados desconocidos explícitos y manejo de errores. Se dejó pendiente confirmar campos reales y se preguntó si la propuesta estaba validada y autorizada. Esta respuesta detallada está resumida aquí porque el registro accesible la conserva de manera incompleta en algunas páginas.

**Lourdes:** «Sí, apruebo la propuesta y autorizo la implementación de “Obtener mis proyectos”. Sigue todo lo que hemos definido y acordado durante este análisis. Recuerda verificar los campos reales de la API y no asumir información que no esté documentada. Cuando termines, revisaremos el resultado antes de pasar a la siguiente skill.»

**C3PO (propuesta aprobada, resumen fiel del flujo):** recuperar `task_type=PROJECT` paginado sin filtrar por estado; conservar resultados parciales; consultar detalles; respetar orden; mostrar campos reales y estados desconocidos sin deducir; no presentar una lista vacía tras un fallo; no mostrar cuerpos de error. El texto íntegro de esta respuesta intermedia no está disponible y por ello se etiqueta como resumen, no como cita.

### Implementación: cambios, comandos y verificaciones

**C3PO (comunicación de implementación):** la skill quedó implementada para revisión; se indicó que consultaba mediante el lanzador común, preservaba orden, clasificaba estados y trataba los errores sin exponer cuerpos. En esa primera revisión se informó que aún no se había hecho una consulta live porque se quería confirmar el esquema desplegado antes de basar la presentación en campos no verificados.

**Comandos registrados en las herramientas de desarrollo (no son mensajes escritos por Lourdes):**

- `python3 -m unittest discover -s skills/obtener-mis-proyectos/tests -v`
- `python3 -m unittest discover -s skills/fourgeeks-api-common/tests -v`
- `python3 /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/quick_validate.py skills/obtener-mis-proyectos`
- `python3 -m py_compile skills/obtener-mis-proyectos/scripts/show_projects.py skills/fourgeeks-api-common/scripts/api_get.py skills/fourgeeks-api-common/scripts/run_api_get.py`
- `git diff --check -- skills/fourgeeks-api-common skills/obtener-mis-proyectos`

**Resultado registrado:** 6 tests de la skill, 7 del cliente común, validación, compilación y diff-check correctos. No se copian salidas de fixtures con valores personales.

**Lourdes (petición literal de verificación):** «Inspecciona todos los aspectos que quedan pendientes de verificar en esta skill y realiza consultas GET reales para comprobar que esta skill funciona correctamente. 
Si detectas diferencias, corrige lo necesario y repite las pruebas.»

**C3PO (resultado literal conservado):** «He ejecutado la skill contra la API desplegada mediante consultas `GET` reales: listado paginado y consulta de detalle para cada proyecto. La respuesta confirmó el sobre de paginación y los campos que la skill utiliza, incluidos estados, cohorte y fechas. La lista terminó correctamente y no hubo fallos de detalle.

El resultado se clasificó en **6 pendientes, 1 entregado, 15 aprobados y 0 rechazados**. No se mostró puntuación: no apareció un campo de puntuación en los datos consultados. No incluyo aquí títulos ni comentarios del listado.

No encontré discrepancias que requirieran cambios. Las 6 pruebas offline de la skill y las 7 del cliente común ya habían pasado; también pasó la validación de la skill. La primera skill queda lista para tu revisión; no he iniciado la segunda.»

### Solicitudes de documentación incorporadas a la cronología

**Lourdes:** «Crea una SKILL_LOG.md en la raíz del workspace. Será un diario de bitacora donde hay que documentar todo el trabajo realizado hasta el momento.

El documento tiene que recoger:
- Conexion de C3PO con la API de 4Geeks:
   - Objetivo de la conexión.
   - Conversación y prompts utilizados.
Configuración de autenticación.

Ubicación de la variable TOKEN_4GEEKS y mecanismo de acceso.»

**C3PO:** informó que creó `SKILL_LOG.md`, documentando objetivo, prompts y decisiones principales, autenticación, ubicación/mecanismo de acceso al token, archivos y verificaciones, sin incluir el token ni datos personales.

**Lourdes:** «Vamos a seguir documentando en este fichero SKILL_LOG.md sin eliminar lo ya escrito.

Añade:
1- Bloque para la creacion de la capa común:
   - Objetivo y motivo de su creación.
   - Conversación, prompts y decisiones tomadas.
   - Estructura de archivos creada y función de cada uno.
   - Funcionamiento de la autenticación y las consultas GET.
   - Endpoints y restriccione
   - Pruebas realizadas y resultados.
   - Estado final de funcionamiento.

2- Bloque para la creación de la primera skill: Obtener mis proyectos
  - Nombre y objetivo.
  ...»

El mensaje original quedó truncado en el extracto disponible después de «...». La ampliación que se registró previamente documenta el resto de requisitos conocidos; no se inventa el final del mensaje perdido.

**C3PO:** añadió el diario cronológico detallado preservando el texto anterior; en la respuesta mostró la bitácora completa.

**Lourdes:** «podrías reajustar los promps originales, y juntarlos para que la conversacion tenga sentido, algunos no tienen sentido».

**C3PO:** reorganizó los prompts y respuestas en el documento, distinguiendo citas literales de resúmenes; la versión íntegra se mostró en la respuesta de ese turno.

### Tramos que no se pudieron recuperar de forma íntegra

No está disponible una transcripción literal completa de todos los turnos entre el inicio del análisis de la skill y la aprobación, ni de todos los mensajes sobre la construcción de la capa común. También se perdieron o truncan algunos resultados de búsqueda/documentación y salidas de herramientas. Se conservaron arriba las intervenciones literales que sí aparecían en las páginas visibles, y se identificaron los resúmenes como resúmenes. En ningún caso se reconstruyeron prompts, preguntas, respuestas o comandos ausentes como si fueran originales.

---

# Apéndice. Solicitud actual de reorganización

**Lourdes:** «Quiero reajustar el contenido actual de SKILL_LOG.md.
El objetivo es que sea una bitácora histórica completa del trabajo realizado, no solamente un resumen técnico.

Mantén los tres bloques principales:
- Conexión de C3PO con la API de 4Geeks.
- Creación de la capa común fourgeeks-api-common.
- Diseño, implementación y verificación de la primera skill «Obtener mis proyectos».

En cada bloque quiero dos partes:
1- Resumen del trabajo
Objetivo, decisiones, configuración, archivos, endpoints, pruebas, resultados y estado final.

2- Conversación completa
Incluye cronológicamente la totalidad de los intercambios que hemos tenido en esa fase:
- Mis mensajes y preguntas.
- Tus respuestas y explicaciones.
- Todos los prompts utilizados.
- Las propuestas iniciales y sus modificaciones.
- Las decisiones y aprobaciones.
- Las correcciones y problemas encontrados.
- Los comandos y resultados relevantes que formaron parte del proceso.

No selecciones únicamente los mensajes importantes ni sustituyas la conversación por resúmenes. Quiero conservar el desarrollo completo, incluyendo las preguntas, dudas y decisiones intermedias.
Identifica en los mensajes quien lo escribe, tú o yo. Y conserva el texto original siempre que esté disponible.
Si no puedes recuperar algún tramo de la conversación, indica expresamente qué parte no has podido recuperar, pero no lo inventes.
Manten las credenciales, TOKEN, y datos personales protegidos [*********]
Conserva la información técnica útil que ya contiene el documento, reorganizándola cuando sea necesario para evitar duplicidades.
Modifica únicamente SKILL_LOG.md y, al terminar, muéstrame el documento completo para revisarlo.»

---

# Bloque 4. Diseño, implementación y verificación de «Obtener trabajo pendiente»

## 4.1 Resumen del trabajo

**Objetivo.** Crear una skill de solo lectura que identifique el trabajo asignado pendiente de Lourdes, explique qué información ofrece la API para entender cada tarea y diferencie con claridad una lista vacía de una consulta fallida o incompleta. La skill abarca proyectos, ejercicios y lecciones, de todas las cohortes. No se consultaron datos de otras personas ni se muestran credenciales, respuestas JSON brutas o campos personales.

**Decisiones funcionales acordadas.**

- Consultar el listado completo de tareas del usuario sin filtrar por `task_status`, porque también hay que detectar estados desconocidos o ausentes. Solicitar los tipos `PROJECT`, `EXERCISE` y `LESSON`, recorrer todas las páginas y conservar el orden de la API; no agrupar por cohorte ni tipo.
- Clasificar después de obtener los resultados. Solo `task_status=PENDING` entra en pendientes. `revision_status` es independiente y no se usa para decidir si una tarea está pendiente.
- Consultar detalle solo para tareas pendientes. No consultar detalle para otros estados ni para las tareas en «Estado no identificar».
- Las tareas con estado ausente o desconocido se ponen bajo «Estado no identificar» y muestran el estado literal o «Sin estado». De ellas se presenta solo lo disponible en el listado.
- Mostrar primero un resumen breve de pendientes (título, ID si existe, tipo y cohorte cuando se reciban) y después el detalle individual en el mismo orden, usando campos disponibles del listado y del detalle: instrucciones si las hay, descripción, fechas, tipo, cohorte y demás datos relevantes. Los campos pertinentes ausentes se marcan «no disponible». Si la API no da información suficiente para determinar qué falta por hacer, indicarlo; no inventar pasos ni requisitos.
- Si falta el título, mostrar «no identificada» e incluir el ID si existe.
- Si falla un detalle, conservar la tarea y los datos del listado, añadir «No se pudo obtener el detalle de esta tarea» e indicar el error seguro cuando esté disponible.
- Decir «No tienes tareas pendientes» solo cuando el listado completo se haya recuperado correctamente y no haya tareas `PENDING`. Si falla la consulta inicial, informar que no se pudo recuperar el listado. Si falla una página posterior, conservar lo obtenido, advertir que es incompleto y no afirmar que no hay pendientes.

**Investigación documental y de código.** Se revisó la referencia local de llamadas API, las rutas permitidas por `fourgeeks-api-common` y el código público de `breatheco-de/apiv2`, en particular `breathecode/assignments/views.py`, `serializers.py`, `urls.py` y `models.py`. No fue necesario realizar una consulta GET a la cuenta durante esta etapa documental.

- Listado: `GET /v1/assignment/user/me/task`. `TaskMeView` toma las tareas del usuario autenticado y admite `task_type`, `task_status`, `revision_status`, `cohort` y otros filtros. Los filtros múltiples se separan por comas. La skill envía `task_type=PROJECT,EXERCISE,LESSON`, paginación `limit`/`offset`, y **no** envía filtro `task_status` ni cohorte. El serializador del listado incluye ID, título, estado de tarea y revisión, tipo, cohorte opcional, descripción, fechas de apertura/lectura/entrega/revisión/creación/actualización y URLs de entrega, entre otros campos. El serializador también puede exponer `user` y `assignment_telemetry`, que se excluyen de la salida.
- Detalle: `GET /v1/assignment/task/{task_id}` (ID numérico). Usa el serializador completo de tarea. No hay garantía contractual de que exista un campo independiente llamado `instructions` o una lista de pasos restantes; la skill muestra lo que realmente llega y explicita cuando no basta.
- Ambos endpoints están en el allowlist GET del cliente común; no se habilitan métodos de escritura.

**Descubrimiento sobre estados (diferencia importante).** La primera implementación de `is_unknown_status` trataba `APPROVED` y `REJECTED` como valores conocidos de `task_status`, siguiendo la referencia general y el diseño de la skill anterior de proyectos. La inspección del modelo fuente de la API mostró que `TaskStatus` define actualmente solo `PENDING` y `DONE`; `RevisionStatus`, en cambio, define `PENDING`, `APPROVED`, `REJECTED` e `IGNORED`. Por tanto, `APPROVED`/`REJECTED` son estados de revisión, no estados de tarea. Se corrigió la skill: `task_status=PENDING` es pendiente, `task_status=DONE` no se muestra, y cualquier otro valor de `task_status` o uno ausente va a «Estado no identificar». El estado de revisión se presenta como dato separado. En la consulta real no hubo valores desconocidos ni ausentes, así que esa rama se comprobó mediante pruebas offline.

**Archivos creados.**

- `skills/obtener-trabajo-pendiente/SKILL.md`: alcance, consultas, clasificación, salida, errores, seguridad y comandos de uso/verificación.
- `skills/obtener-trabajo-pendiente/scripts/show_pending_work.py`: consulta paginada usando `fourgeeks-api-common`, clasificación posterior al listado, detalle únicamente para pendientes y render de salida segura. La respuesta estructurada se captura y procesa en memoria; los campos `user` y `assignment_telemetry` se omiten.
- `skills/obtener-trabajo-pendiente/tests/test_show_pending_work.py`: pruebas unitarias offline con respuestas simuladas; no llaman a la API.

**Pruebas offline y controles.** Las nueve pruebas pasaron, cubriendo formato de páginas y orden, ausencia de filtro de estado, fallos de página posterior, listado simple no verificable como completo, independencia de `revision_status`, llamada de detalle solo para pendientes, estado desconocido/ausente, título ausente, mensaje de lista vacía y omisión de datos personales/telemetría. También pasaron `py_compile`, `quick_validate.py` y `git diff --check`. Se verificó que el validador debía invocarse como `python3` porque el comando `python` no existe en este entorno.

**Consultas GET reales y resultado.** A petición de Lourdes, se ejecutó la skill contra la API real, con salida de verificación agregada y sin mostrar títulos, nombres de cohorte, contenido de tareas, datos personales, credenciales, tokens ni JSON bruto. El listado paginado devolvió 112 tareas en total: `EXERCISE=88`, `LESSON=2`, `PROJECT=22`; estados `DONE=90`, `PENDING=22`. Se comprobó que se intentó obtener detalle para exactamente los 22 IDs pendientes, y para ninguno de los otros 90. La respuesta se procesó internamente; los datos individuales no se reprodujeron en la bitácora. No se encontró caso live con estado desconocido o ausente. No se informa de pruebas live de los flujos de error, pues no ocurrieron durante la consulta real.

Tras descubrir la discrepancia de enumeraciones, se actualizó el código y `SKILL.md`; se repitieron las pruebas offline y la validación, que volvieron a pasar. Se volvió a ejecutar la consulta live y se confirmó el mismo resultado agregado y que el número/IDs de llamadas de detalle coincidían exactamente con los pendientes.

**Estado final.** Skill implementada y comprobada con pruebas offline y consulta GET real. No se modificó la capa común ni otra skill en esta fase. La consulta live confirmó los tres tipos solicitados y el enrutamiento de detalles correcto para los datos observados; estados desconocidos/ausentes y fallos quedan cubiertos por pruebas simuladas, no por un caso real. La skill no marca como completada ninguna tarea académica: solo informa del estado de la API.

## 4.2 Conversación cronológica recuperable

Se mantienen como citas literales los mensajes de Lourdes disponibles en el historial de esta fase. Las respuestas intermedias de C3PO se resumen cuando no se dispone de su texto literal completo; esos resúmenes no pretenden ser citas. No se inventan turnos ausentes.

### Solicitud de investigación y definición inicial

**Lourdes:** «Pasamos a la siguiente SKILL, que tendra como titulo **Obtener trabajo pendiente**, y su objetivo será identificar el trabajo que tengo pendiente e indicarme específicamente qué me falta por completar.
Para ello:
- Investiga en la documentación de la API qué endpoints permiten obtener mis tareas y actividades pendientes, qué parámetros necesitan y qué información devuelven.
- Explícame cómo podemos identificar qué está pendiente y qué información permite saber qué falta por completar.
- Propón la estructura básica de la skill, los archivos necesarios y las pruebas que deberíamos realizar.
- Guíame mediante preguntas sencillas, de una en una, para decidir cómo va a funcionar.
No modifiques ni crees archivos todavía. Primero quiero definir contigo la estructura y el funcionamiento de la skill.»

**C3PO (respuesta resumida):** revisó las referencias locales y propuso el listado `GET /v1/assignment/user/me/task`, el detalle `GET /v1/assignment/task/{task_id}`, y opcionalmente actividad/cohortes para contexto. Explicó que `task_status=PENDING` sería el criterio explícito, separado de revisión, y que la documentación no prometía un campo universal con pasos restantes. Propuso `SKILL.md`, un posible helper y pruebas offline; preguntó si se incluirían todos los tipos.

### Tipos de tarea, estado y alcance de detalle

**Lourdes:** «Quiero que incluya todos los tipos de tareas asignadas: proyectos, ejercicios y lecciones.
Identifica como pendientes las tareas cuyo `task_status` sea `PENDING`, sin confundirlo con el estado de revisión (`revision_status`).
Quiero poder ver qué tengo pendiente independientemente del tipo de actividad.»

**C3PO:** confirmó incluir `PROJECT`, `EXERCISE` y `LESSON`, y que solo `task_status=PENDING` sería pendiente. Preguntó si debía consultar el detalle de cada pendiente.

**Lourdes:** «Quiero que consultes el detalle de cada tarea pendiente para mostrar:
- instrucciones,
- descripción y
- cualquier información que permita identificar qué falta por completar.

Para las tareas que no estén pendientes, no será necesario consultar el detalle, ni mostrarlas.
No inventes requisitos ni deduzcas pasos que la API no proporcione.
Si la información disponible no permite determinar qué falta por hacer, indícalo expresamente.»

**C3PO:** confirmó los límites: solo detalles para pendientes, no inferir pasos y avisar cuando falte información; preguntó qué hacer si falla un detalle.

**Lourdes:** «Muestrala, pero con una nota: «No se pudo obtener el detalle de esta tarea».
No descartes la tarea ni inventes las instrucciones que falten.
Indica el error cuando sea posible.»

**C3PO:** acordó conservar la tarea, mostrar la nota y el error seguro disponible; preguntó si se incluirían todas las cohortes.

### Cohortes, listado vacío y orden

**Lourdes:** «Quiero incluir las tareas pendientes de todas mis cohortes, no solo de la activa.
Además, muestra la cohorte a la que pertenece cada tarea, siempre que la API proporcione esa información.»

**C3PO:** confirmó el alcance y preguntó qué decir si no hay pendientes.

**Lourdes:** «Sí. Pero hay que diferenciar de no tener tareas pendientes de que la consulta falle o queda incompleta, en este ultimo caso informa del error y no afirmes que no hay tareas pendientes.»

**C3PO:** confirmó que el mensaje de ausencia solo se usaría tras listado completo; preguntó el orden.

**Lourdes:** «Orden recibido por la API»

**C3PO:** confirmó mantener el orden de todas las páginas y preguntó qué campos mostrar en el resumen frente al detalle.

### Formato de respuesta y campos ausentes

**Lourdes:** «Quiero ambas opciones:
- Primero una salida breve con un resumen de todas las tareas pendientes y,
- Después un apartado detallado de cada tarea con toda la información disponible en la API, incluidas instrucciones, descripción, fechas, tipo y cohorte.
Así podré consultar rápidamente qué tengo pendiente y ampliar la información de cada tarea cuando lo necesite.
No inventes información que la API no proporcione.»

**C3PO:** acordó resumen y detalle manteniendo el orden; preguntó si el resumen debía incluir tipo/cohorte.

**Lourdes:** «Perfecto»

**C3PO:** confirmó título, tipo y cohorte cuando existieran; preguntó por tareas sin título.

**Lourdes:** «Si no trae titulo, pon "no identificada", además del ID»

**C3PO:** acordó el marcador y preguntó qué hacer con otros campos ausentes.

**Lourdes:** «Marcarlo como «no disponible»»

**C3PO (respuesta resumida):** presentó el diseño acumulado y preguntó cómo tratar estados ausentes/desconocidos.

### Estados desconocidos y detalles limitados

**Lourdes:** «Sí, excluye esas tareas y agrúpalas en un apartado separado llamado «Estado no identificar»
Muestra el estado literal que devuelva la API o indica «Sin estado» si no proporciona ninguno»

**C3PO:** acordó el apartado y preguntó si debía consultar detalles de esas tareas.

**Lourdes:** «Sí. Muestra únicamente los datos disponibles en el listado.»

**C3PO (respuesta resumida):** confirmó que no consultaría detalles en estados ausentes/desconocidos. Recapituló rutas/campos documentados y propuso comprobar cualquier cuestión pendiente antes de implementar.

### Verificación documental y propuesta final

**Lourdes:** «Investiga que necesitas para resolver las dudas pendientes que expones.
Busca en la documentacion. Si necesitas hacer alguna consulta GET para comprobarlo, puedes hacerlo.
Si no consigues verificarlo, explícame qué necesitas para poder solucionarlo.»

**C3PO (respuesta resumida):** buscó en el código fuente público de la API los handlers, serializers, modelos y rutas de Assignments. Confirmó que el filtro `task_type` acepta lista separada por comas, que listado y detalle están disponibles en la allowlist común y que los serializadores exponen cohorte, fechas, descripción y estados. Indicó que el detalle no garantiza un campo estructurado de instrucciones/pasos; no realizó GET a la cuenta.

**Lourdes:** «Perfecto. Prepara la propuesta final de estructura y funcionamiento de «Obtener trabajo pendiente», teniendo en cuenta todas las decisiones que hemos tomado.
Importante: no filtres el listado por `task_status=PENDING`, porque también necesitamos identificar y mostrar las tareas cuyo estado sea desconocido o no esté disponible. La clasificación debe realizarse después de recuperar los resultados.
Preséntame la propuesta y las pruebas previstas. No crees ni modifiques archivos todavía.»

**C3PO:** presentó el flujo sin filtro de estado, clasificación posterior, estructura `SKILL.md`/helper/tests y casos de prueba, sin crear archivos.

### Aprobación e implementación

**Lourdes:** «Puedes comenzar la implementación siguiendo lo acordado.»

**C3PO:** creó `skills/obtener-trabajo-pendiente/SKILL.md`, `scripts/show_pending_work.py` y `tests/test_show_pending_work.py`. El helper pagina las consultas del endpoint de listado con los tres tipos solicitados, no pasa `task_status`, clasifica una vez recuperados los resultados, pide detalles solo a pendientes y omite los campos personales/telemetría. Las pruebas offline iniciales pasaron: 9 tests; también pasaron compilación y validación de skill. En ese punto no se había hecho consulta live en esta fase.

### Prueba live solicitada y corrección

**Lourdes:** «Inspecciona todos los aspectos que quedan pendientes de verificar y realiza consultas GET reales para comprobar que la skill funciona correctamente.
Comprueba especialmente que recupera los tres tipos de tareas, identifica correctamente los estados y consulta los detalles únicamente de las tareas pendientes.
Si detectas diferencias, corrige lo necesario y repite las pruebas.
No muestres datos personales ni credenciales ni TOKENs.»

**C3PO (resultado resumido sin datos de tarea):** realizó consultas GET a través del cliente común y recuperó 112 registros en total: 88 ejercicios, 2 lecciones y 22 proyectos; 90 tenían `task_status=DONE`, 22 `PENDING`. Se intentó consultar detalle para exactamente 22 IDs, correspondientes a los pendientes. No aparecieron estados desconocidos/ausentes en esa cuenta. No se imprimieron valores personales, token o JSON bruto.

La revisión del código fuente detectó que `task_status` solo define `PENDING`/`DONE`, mientras `revision_status` define `PENDING`/`APPROVED`/`REJECTED`/`IGNORED`. El clasificador inicial reconocía `APPROVED`/`REJECTED` como si pudieran ser estados conocidos de tarea; eso no correspondía al modelo de la API. Se corrigió `is_unknown_status` para reconocer solo `PENDING` y `DONE` como valores de `task_status`, se actualizó `SKILL.md` y se añadió una prueba para `task_status=APPROVED` como desconocido. No se mezcló `revision_status` con la clasificación de pendientes.

**C3PO (resultado tras corrección):** repitió la consulta GET real; recuperó los mismos totales agregados, confirmó llamadas de detalle solo para los pendientes y comprobó que el texto de salida no incluía campos personales ni términos de credencial. Las 9 pruebas offline, validación de skill, compilación y `git diff --check` pasaron de nuevo. La cobertura de estados desconocidos/ausentes siguió siendo offline porque la respuesta real no contenía esos casos.

### Límites y fidelidad histórica

Los mensajes de Lourdes de esta fase se conservaron en el historial compacto como textos literales y se reproducen arriba. Las respuestas de C3PO no se conservaron todas palabra por palabra; las identificadas como «respuesta resumida» son recapitulaciones de los turnos visibles y resultados técnicos, no citas. No se recuperaron cuerpos API ni se reproducen identificadores de tareas, títulos, nombres de cohortes, descripciones, URLs de entrega, usuarios, secretos o tokens. No se hicieron cambios a `fourgeeks-api-common` durante esta implementación.

---

# Bloque 5. Diseño, creación, verificación y adaptación de «Obtener resumen del progreso»

## 5.1 Resumen del trabajo

**Objetivo.** Crear una skill de solo lectura que resuma las tareas asignadas por cohorte y tipo, calcule un porcentaje de tareas entregadas con denominador explícito, presente por separado las calificaciones de proyectos y resuma la actividad registrada sin confundir eventos con avance académico. El diseño y la implementación se limitaron a los datos que las consultas GET autorizadas pudieran entregar; no se alteró autenticación ni se intentaron eludir permisos.

**Prompts y decisiones funcionales.** La usuaria pidió investigar la API, proponer estructura y pruebas sin crear archivos antes de aprobación, y guiar el diseño con decisiones progresivas. Las decisiones aprobadas fueron:

- Incluir todas las cohortes cuando los datos de origen las permitan identificar; separar la vista por cohorte y permitir un total global basado en sumas comparables. No promediar porcentajes de cohortes ni asignar sin evidencia tareas o eventos a cohortes.
- Separar **Progreso de tareas** de **Actividad registrada**. Los eventos no se emplean para calcular porcentajes académicos.
- Calcular el porcentaje de tareas entregadas como `DONE / (PENDING + DONE)`. El porcentaje no es una métrica oficial del curso ni se altera con calificaciones. Si no existen estados identificables con denominador positivo, mostrar «Avance no disponible».
- Mostrar estados de tarea ausentes o desconocidos aparte; incluir tareas sin cohorte identificable en «Cohorte no disponible», en totales globales cuando corresponda, pero no en porcentajes individuales por cohorte.
- Mostrar recuentos de revisión `PENDING`, `APPROVED` y `REJECTED` solo para tareas `PROJECT`, como indicadores independientes del porcentaje de tareas entregadas. Una misma tarea puede estar `DONE` y tener estado de revisión.
- Incluir `QUIZ` si aparece entre las tareas asignadas y tratarlo como tipo independiente; su progreso depende de `task_status`, no se considera trabajo calificado.
- Para actividad, resumir eventos por tipo y cohorte solo cuando la respuesta identifique claramente esos atributos. Eventos sin cohorte explícita/inequívoca irían en «Cohorte no disponible» si se pudiera recuperar la actividad.
- La usuaria aprobó la propuesta e implementación; posteriormente, al detectarse HTTP 403 en cohortes y actividad, autorizó mantener las funciones que sí operan y adaptar la skill a esas limitaciones.

**Investigación de API.** Se revisaron referencias locales de rutas y campos, y código fuente público de `breatheco-de/apiv2`, incluyendo las vistas de Admissions y Activity y sus rutas. El cliente común permite GET a `/v1/assignment/user/me/task`, `/v1/admissions/academy/cohort/me` y `/v1/activity/me`, pero que una ruta esté en allowlist no garantiza autorización de la cuenta. En el código consultado, el endpoint de cohortes usa `read_single_cohort` y limita la lista a cohortes vinculadas al usuario y academia del contexto. La vista de actividad usa `read_activity`; admite filtros tales como `cohort` (slug) y tipo (`slug`).

**Estructura de archivos de la skill.**

- `skills/obtener-resumen-progreso/SKILL.md`: alcance, definiciones, restricciones de interpretación, rutas, límite de acceso y comandos de ejecución/verificación.
- `skills/obtener-resumen-progreso/scripts/show_progress.py`: llama al listado paginado de tareas por la capa común, procesa JSON en memoria y renderiza recuentos/porcentajes/revisiones sin exponer campos personales; no llama a los endpoints de cohortes o actividad tras la adaptación por 403.
- `skills/obtener-resumen-progreso/tests/test_show_progress.py`: pruebas unitarias offline de paginación, estados/tipos, porcentaje, proyecto/revisión, cohortes, limitaciones de actividad y salida sin inferencias.

**Pruebas offline y controles.** Inicialmente se registraron 4 pruebas offline; después de adaptar la skill a la restricción de acceso, se ampliaron a 5. La última ejecución confirmada pasó 5 pruebas. También pasó `quick_validate.py` y `py_compile`. Durante una primera ejecución se detectó un test que seguía usando la firma antigua de `render_tasks`; se ajustó la llamada del test y la suite volvió a pasar. No se alteró la capa común ni el mecanismo de autenticación.

**Consultas GET reales y resultados.** La primera ejecución live de la skill obtuvo 112 tareas: 88 `EXERCISE`, 2 `LESSON` y 22 `PROJECT`; 90 tareas `DONE` y 22 `PENDING`. Por cohorte/tipo se pudieron calcular porcentajes, y los proyectos se contaron por separado según `revision_status`. En el total reportado en esa prueba aparecieron 15 proyectos `APPROVED`, 7 `PENDING` y 0 `REJECTED`. Los endpoints de cohorte y actividad respondieron HTTP 403; se repitieron llamadas directas de control, incluyendo filtros de consulta, y persistió HTTP 403. La API aceptó en esa misma ventana `GET /v1/admissions/user/me` y el listado de tareas, lo que prueba que el cliente y token funcionaban para esos recursos, pero no determina por sí solo si la restricción se debe al permiso `read_single_cohort`/`read_activity`, al contexto de academia u otra política del servicio.

A solicitud de la usuaria se hizo una segunda prueba live tras adaptar la implementación. El listado de tareas funcionó y generó por cohorte/tipo los porcentajes y recuentos de revisión. La salida indicó explícitamente que las cohortes mostradas proceden solo de tareas que las identifican, no enumeró cohortes sin tareas y no afirmó que la lista fuera completa. La sección **Actividad registrada** indicó HTTP 403, no mostró recuentos y aclaró que no se infieren eventos a partir de tareas ni se consideran porcentaje de avance. No se mostraron datos personales ni cuerpos JSON. No se repitieron consultas a los endpoints restringidos en esta segunda verificación.

**Cambios realizados para adaptar la skill a HTTP 403.** Se retiraron de `main()` las consultas automáticas a `GET /v1/admissions/academy/cohort/me` y `GET /v1/activity/me`, evitando llamadas conocidas como fallidas. Se eliminó la lógica que habría agregado cohortes procedentes del endpoint separado. El render ahora usa exclusivamente la cohorte explícita incluida en cada tarea; añade una advertencia de que no enumera cohortes sin tareas y no garantiza lista completa. La sección de actividad se conserva como aviso de no disponibilidad por HTTP 403, sin mostrar cero eventos, contarlos desde tareas o inferir actividad. Se actualizó `SKILL.md` para reflejar estas restricciones y se sustituyó el test de resumen de actividad simulado por pruebas del aviso de acceso denegado y ausencia de inferencia. Se ajustó `call_api()` para conservar únicamente el código HTTP numérico del diagnóstico saneado; el cambio no toca credenciales ni controles de autenticación.

**Límites funcionales actuales.** Funciona el progreso de tareas recuperadas, agrupado por cohorte solo cuando la tarea lo identifica, por tipo, el porcentaje calculado sobre estados `PENDING`/`DONE`, el reporte separado de estados desconocidos y las tres métricas de revisión de proyectos. La suma global incluye registros recuperados, pero no convierte esos datos en porcentaje oficial de curso. No se puede enumerar cohortes sin tareas ni confirmar que toda la relación de cohortes esté representada. La actividad real no está disponible mientras la API devuelva 403: la skill no puede ofrecer recuentos de eventos por tipo/cohorte. Los recuentos de tareas y de actividad no se mezclan.

**Estado final.** Skill implementada, probada offline y ejecutada contra la API real para el endpoint de tareas. La salida live verificó las funcionalidades que siguen disponibles y mostró las limitaciones acordadas. Sin cambios de seguridad, autenticación, credenciales ni operaciones de escritura.

## 5.2 Conversación cronológica recuperable

El historial compacto conserva prompts completos de las decisiones finales y resúmenes de algunos turnos previos. Las citas siguientes se reproducen literalmente cuando el texto está disponible; las respuestas de C3PO que no se conservaron íntegras se identifican como resumen, no como cita. No se reconstruyen prompts ausentes.

### Solicitud inicial y diseño

**Lourdes:** «Pasamos a la siguiente skill, “Obtener resumen del progreso”. Investiga qué datos permite recuperar la API para resumir el progreso de tareas y actividad, explícame qué indicadores se pueden construir sin inventar información y propón estructura y pruebas. No crees ni modifiques archivos todavía; guíame con preguntas sencillas, de una en una.»

> Nota: esta formulación recoge el contenido recuperable del objetivo inicial; el historial previo fue compactado y no se conserva aquí el texto literal completo del primer prompt.

**C3PO (respuesta resumida):** investigó endpoints de tareas, cohortes y actividad, y explicó que la API no ofrecía una métrica directa verificada de porcentaje del curso. Se propuso separar actividad registrada de avance de tareas y explicitar cualquier cálculo propio.

**Lourdes (decisión literal recuperable):** pidió incluir todas las cohortes y separarlas, con una visión global solo para recuentos comparables; no promediar porcentajes ni asignar tareas sin cohorte. Para actividad, confirmó atribución solo si la respuesta identificaba claramente la cohorte; de lo contrario, «Cohorte no disponible».

**C3PO (respuesta resumida):** presentó como opciones recuentos de estados y porcentajes por cohorte, actividad independiente y totales globales calculados sobre datos comparables. No creó archivos durante el diseño.

**Lourdes:** «Sí, me parece bien la propuesta. Con respecto a las tareas sin cohorte o con estados desconocidos, muéstralas por separado. Las calificaciones de los proyectos se mostrarán como indicadores independientes y no modificarán el porcentaje de avance. Si no hay tareas con estados identificables para calcular el porcentaje, indica que el avance no está disponible.»

**C3PO (respuesta resumida):** definió `DONE / (PENDING + DONE)` como cálculo por cohorte, estados desconocidos fuera del denominador, cohortes no disponibles aparte y calificaciones independientes. Aclaró que no había una métrica oficial de porcentaje de curso verificada.

**Lourdes:** «En un apartado independiente llamado «Cohorte no disponible». Inclúyelos también en los totales globales cuando corresponda, pero no los atribuyas a ninguna cohorte ni alteres los porcentajes individuales de cada una.»

**C3PO:** confirmó que las tareas sin cohorte identificable se colocarían bajo «Cohorte no disponible», se incluirían en totales globales cuando correspondiera y no afectarían porcentajes individuales. Propuso el denominador explícito y aclaró que el porcentaje no era una métrica curricular oficial.

**Lourdes:** «Sí, siempre que aparezcan como tareas asignadas en la API. Identifícalos como un tipo de actividad independiente. Su progreso dependerá de `task_status` (PENDING o DONE), pero no los contabilices como trabajos calificados, ya que las calificaciones corresponden únicamente a los proyectos.»

**C3PO:** confirmó incluir `QUIZ` como tipo separado si aparece entre las tareas asignadas, contarlo por `task_status` y excluirlo de recuentos de revisión de proyectos.

**Lourdes:** «Prefiero un resumen con el número de eventos por tipo y cohorte. Incluye los tipos de actividad y los recuentos que la API permita identificar. Mantén este apartado separado del progreso de tareas y no interpretes el número de eventos como porcentaje de avance académico.»

**C3PO:** confirmó actividad agregada por tipo y cohorte, separada de tareas y porcentajes, limitada a campos que la respuesta identifique.

### Propuesta aprobada y ajuste de indicadores de revisión

**C3PO (propuesta final, registrada en el historial):** propuso consultas de tareas paginadas con `task_type=PROJECT,EXERCISE,LESSON,QUIZ`, cohortes y actividad; separó progreso de tareas, revisiones solo para proyectos y actividad independiente; describió archivos `SKILL.md`, helper y tests offline; indicó paginación, datos en memoria, errores parciales y ausencia de métrica oficial curricular. Este bloque se resume porque el mensaje íntegro de C3PO está disponible en el historial de la conversación, pero no en la parte retenida por la compactación que dio origen a esta bitácora.

**Lourdes:** «La propuesta me parece correcta. Solo quiero ajustar un detalle. Añade el recuento de proyectos pendientes de revisión (`revision_status=PENDING`), junto a aprobados y rechazados. Los tres indicadores deben ser independientes del porcentaje de tareas entregadas. El resto de la propuesta queda aprobada. Implementa la propuesta actualizada.»

**C3PO (respuesta de confirmación previa a implementación):** registró el ajuste de revisión pendiente junto con aprobados/rechazados, independiente del porcentaje. El historial preservado señala que la implementación quedó pendiente en ese momento; a continuación se registran los cambios ejecutados tras la aprobación.

### Implementación inicial y prueba real

**C3PO (resultado de implementación):** creó `SKILL.md`, `scripts/show_progress.py` y `tests/test_show_progress.py`. El helper consulta tareas, cohortes y actividad, procesa JSON en memoria, presenta avance por cohorte/tipo y revisión de proyectos, y agrupa actividad por tipo/cohorte. Cuatro pruebas offline pasaron inicialmente, así como validación de skill y compilación.

**Lourdes:** «Inspecciona todos los aspectos que quedan pendientes de verificar y realiza consultas GET reales para comprobar que la skill funciona correctamente. Comprueba especialmente el progreso por cohorte y tipo, los porcentajes de entrega, las calificaciones de los proyectos y el resumen de actividad registrada. Si detectas diferencias, corrige lo necesario y repite las pruebas. No muestres datos personales.»

**C3PO (resultado técnico resumido):** la ejecución real recuperó 112 tareas y produjo grupos por cohorte/tipo, porcentajes y revisiones de proyectos. Sin embargo, `GET /v1/admissions/academy/cohort/me` y `GET /v1/activity/me` respondieron HTTP 403. Las secciones de cohorte/actividad no pudieron comprobarse en esa ejecución. Las pruebas offline pasaron. El helper se ajustó para mostrar solo el código HTTP numérico seguro del error. El mensaje original de resultados contenía los datos desglosados por cohortes; esos nombres no se reproducen en esta bitácora para minimizar datos personales.

**Lourdes:** «Investiga por qué se rechazan esas dos consultas. Comprueba los permisos, la autenticación, los parámetros y cualquier requisito específico de esos endpoints. Quiero saber si es un problema de acceso de mi cuenta o si esos recursos requieren permisos adicionales. No modifiques la seguridad de la capa común, no cambies credenciales ni busques alternativas que impliquen operaciones de escritura. Si no es posible acceder a esos endpoints, explícame qué funcionalidades podemos mantener y cuáles quedarían limitadas. No confundas los recuentos de tareas con los eventos de actividad. No realices cambios todavía.»

**C3PO (investigación y conclusión resumida):** verificó que `GET /v1/admissions/user/me` y el listado de tareas funcionaban con la misma capa/token, lo que descarta fallo general de autenticación, pero no confirma permisos específicos. Repitió cohortes con `educational_status=ACTIVE` y actividad con filtro de cohorte; ambas continuaron en HTTP 403. Revisó código fuente público de Admission/Activity: Cohorte requiere `read_single_cohort`, actividad requiere `read_activity`; la vista de cohorte limita resultados a cohortes de la persona en el contexto de academia. La vista de actividad admite `cohort` por slug, no ID. Se concluyó que el problema era compatible con permisos o contexto de academia, pero el 403 no permitía determinar cuál sin detalle del operador/API. No se modificó ningún archivo ni seguridad. Se recomendó conservar las funciones basadas en tareas, y marcar cohortes completas y eventos como limitados/no disponibles.

### Adaptación a HTTP 403 aprobada

**Lourdes:** «Perfecto. Conserva todas las funcionalidades que funcionan correctamente y adapta el resumen a las limitaciones actuales. No modifiques la autentificacion ni intentes eludir permisos. Actualiza la propuesta».

**C3PO (propuesta actualizada):** indicó que el progreso se basaría en tareas recuperadas y cohortes explícitas de esos registros; revisiones quedarían separadas; el endpoint de cohortes dejaría de ser dependencia y no se prometería una lista completa; la actividad mostraría no disponible por denegación, sin recuentos cero o inferencias; omitiría llamadas automáticas conocidas como fallidas.

**Lourdes:** «Perfecto. Aplica las actualizaciones acordadas a la implementación existente de la skill «Obtener resumen del progreso».»

**C3PO (cambios implementados):** retiró llamadas a `GET /v1/admissions/academy/cohort/me` y `GET /v1/activity/me`; dejó la agrupación de tareas basada solo en cohortes identificadas por el propio registro; añadió advertencia sobre cohortes no enumeradas y ausencia de garantía de lista completa; mantuvo actividad como limitación explícita de HTTP 403 y prohibió inferir eventos desde tareas. Actualizó las pruebas y `SKILL.md`. Una prueba falló inicialmente por usar la firma antigua del helper; se actualizó el test y la repetición pasó. El total final fue 5 pruebas offline, `quick_validate.py` y `py_compile` correctos.

**Lourdes:** «Comprueba la implementación actualizada de «Obtener resumen del progreso» mediante una ejecución real contra la API. Comprueba también que la salida refleja las limitaciones acordadas.»

**C3PO (verificación real):** ejecutó el helper final. El listado de tareas tuvo éxito y devolvió 112 registros; la salida incluyó desglose por las cohortes identificadas en tareas, por tipo, porcentajes y recuentos de revisión. La salida advirtió que no enumera cohortes sin tareas ni garantiza lista completa. **Actividad registrada** indicó HTTP 403 y no mostró recuentos ni inferencias desde tareas. Para esta ejecución no se llamaron los endpoints restringidos. No se mostraron datos personales. Los totales agregados observados fueron 90 `DONE`, 22 `PENDING`, revisiones de proyectos 15 `APPROVED`, 7 `PENDING`, 0 `REJECTED`; se omiten nombres/detalles por cohorte.

## 5.3 Límites de recuperación histórica

Los prompts finales de diseño, solicitudes de investigación, autorización de implementación, diagnóstico de HTTP 403 y adaptación se conservaron literalmente arriba. Parte de los primeros turnos de diseño y algunas respuestas de C3PO provienen de un resumen de sesión y no pueden verificarse como transcripción palabra por palabra; por eso se marcan como resumidos. No se inventaron prompts ni resultados para cubrir esos huecos. Las respuestas JSON reales, identificadores personales y nombres de cohorte no se copian en esta bitácora.

---

# Bloque 6. Diseño, investigación, implementación y verificación de «Consultar feedback de mis proyectos»

## 6.1 Resumen del trabajo

**Objetivo.** Crear una skill que recupere y organice comentarios, observaciones, valoraciones y resultados que dejan docentes al corregir los proyectos propios de Lourdes. El trabajo comenzó investigando las rutas de revisión de código, pero se reorientó al descubrir que la evaluación docente de 4Geeks está reflejada en los campos de la tarea asignada. Se distingue explícitamente de las revisiones automáticas/relacionadas con código de Rigobot.

**Prompts y decisiones cronológicas.**

1. Lourdes pidió investigar la API antes de crear archivos para una nueva skill llamada **«Consultar feedback de mis proyectos»**: localizar endpoints, parámetros y respuestas; determinar si se pueden obtener comentarios, puntuaciones, estados, recomendaciones y fechas; proponer el diseño sin implementar ni ampliar allowlist.
2. La investigación inicial encontró rutas de CodeRevision de Rigobot, incluida una ruta personal por tarea, y referencias a rutas de academia. Se aclaró que la documentación/código no confirmaba que esas revisiones fueran la corrección docente de proyectos ni que incluyeran todos los campos buscados.
3. Lourdes prefirió investigar primero la ruta personal de revisión de código y preguntó qué cambio concreto de allowlist, requisitos y salvaguardas serían necesarios. Se propuso una ruta con ID numérico y alcance personal, sin rutas de academia ni escritura. En esa fase no se hizo la consulta ni se cambiaron archivos.
4. Lourdes autorizó añadir la ruta personal numérica de revisión y realizar una prueba GET, manteniendo autenticación y controles existentes. Se intentó la consulta por la capa común: el GET devolvió HTTP 404 y el cuerpo fue suprimido. Esa prueba no confirmó campos ni contrato de respuesta; la ruta resultó no ser la vía adecuada para el feedback docente que se buscaba.
5. Lourdes cambió el enfoque expresamente: investigar dónde guarda la plataforma las evaluaciones de profesores, qué endpoints sirven para leerlas, qué campos devuelven, permisos y disponibilidad en la capa común. Prohibió entonces ampliar allowlist o modificar archivos.
6. La investigación de código de `BreatheCo-de/apiv2` identificó la ruta personal de detalle de tarea y el serializador de tareas. Se propuso que `description` contiene el feedback de corrección, `revision_status` su resultado y `reviewed_at` la fecha. Lourdes autorizó comprobarlo con una tarea aprobada mediante GET y sin exponer datos personales.
7. El GET de detalle de una tarea aprobada confirmó `description` con comentario docente, `revision_status=APPROVED` y `reviewed_at` presente. El comentario no coincidía con título ni `associated_slug`; se concluyó para ese caso que `description` era feedback de corrección, no la descripción original del proyecto.
8. Lourdes pidió continuar con análisis y definición de la skill; recibió un borrador funcional. Después autorizó la creación.

**Hallazgos de API.**

- Lista de tareas personales/proyectos: `GET /v1/assignment/user/me/task`, con `task_type=PROJECT`, `limit` y `offset`. La ruta ya estaba habilitada en la capa común.
- Detalle personal de tarea: `GET /v1/assignment/task/{task_id}`, donde el ID debe ser numérico. Esta ruta también estaba ya habilitada. La vista personal filtra el detalle por la identidad autenticada, y evita consultar tareas ajenas.
- El serializador real de detalle incluye `title`, `task_status`, `description`, `revision_status`, `reviewed_at`, `delivered_at`, `opened_at`, `read_at`, `created_at`, `updated_at`, `task_type`, `cohort`, `user` y `assignment_telemetry`, entre otros. La skill solo necesita título, estados, feedback y fecha; debe excluir `user`, telemetría y datos personales.
- `description` guarda el texto de feedback docente en los casos live observados; `revision_status` da el resultado de revisión (`APPROVED`, `REJECTED`, `PENDING`, entre los valores de la tarea); `reviewed_at` aporta fecha. No se encontró campo independiente de puntuación numérica ni campos separados de recomendación/observación. Los comentarios pueden ser breves o más específicos, pero no se debe generalizar ni inventar una valoración.
- Estas rutas son distintas de `.../coderevision` que reenvía consultas a Rigobot. La prueba de la ruta personal de CodeRevision dio HTTP 404; no debe usarse para esta skill ni confundirse con la corrección docente guardada en la tarea.
- No se usan rutas de academia, no se requiere la capacidad de staff `read_assignment` para la vista de tarea propia y no hay operaciones de escritura.

**Estructura creada.** Se creó únicamente `skills/consultar-feedback-proyectos/SKILL.md`. El documento define activación/alcance, consulta paginada, obtención de detalles por cada ID de la lista personal, presentación de feedback real, estados/fechas, ausencia de puntuaciones verificadas, errores parciales y tratamiento de privacidad. No se añadió helper ni suite de tests propia; el flujo usa directamente la capa común existente y sus dos rutas ya permitidas. No se amplió allowlist para implementar esta skill.

**Verificaciones offline y validación.** Se comprobó por inspección que ambas rutas de tarea ya estaban en la allowlist común. La ruta numérica personal de CodeRevision había sido añadida en `skills/fourgeeks-api-common/scripts/api_get.py` durante la fase experimental autorizada; se comprobó que solo coincidía con IDs numéricos personales y rechazaba rutas de academia. La skill nueva no utiliza esa ruta. `quick_validate.py /root/.openclaw/workspace/skills/consultar-feedback-proyectos` devolvió **«Skill is valid!»**. No hay helper propio que requiera pruebas unitarias.

**Consultas reales y resultados, sin reproducir comentarios particulares.**

- GET de prueba de CodeRevision personal por tarea: HTTP 404, cuerpo suprimido; no se obtuvo feedback docente de esa vía.
- GET personal de detalle de tarea previamente aprobada: HTTP exitoso; confirmó campos `description`, `revision_status` y `reviewed_at`. El valor de `description` era un comentario, no el título ni el slug del proyecto. No se reproducen comentarios ni identificadores.
- Ejecución completa posterior: el listado paginado de proyectos devolvió **22** tareas de tipo proyecto y los **22** detalles se recuperaron correctamente (**0 errores**). Resultados agregados: **15 aprobados**, **7 pendientes**, **0 rechazados**. Los 15 aprobados tenían comentarios en `description` y fechas `reviewed_at`; los 7 pendientes no tenían `description` ni `reviewed_at`. La respuesta mostró comentarios de longitud y detalle variables; no se copiaron ni se muestran en este bloque. No aparecieron puntuaciones numéricas independientes ni recomendaciones en campos separados.
- Se comprobó en la ejecución que los errores de detalle se aíslan por proyecto y el flujo continúa; en esta ejecución no hubo errores para validar un fallo live. La ruta de error mantiene mensajes saneados del cliente común y no expone cuerpos. El manejo de errores parciales está documentado en la skill, pero no se simula con una API de escritura ni se modifican datos.
- No se imprimieron IDs, datos personales de `user`, telemetría, URLs de repositorios ni JSON bruto en el informe final.

**Estado final.** Skill creada y validada estructuralmente. La ejecución live confirmó paginación, detalles, feedback en `description`, estados y fechas, así como el tratamiento de los siete proyectos sin feedback/fecha registrados como pendientes. No se inventan valoraciones ni recomendaciones. La nueva skill no necesitó ampliar allowlist. La investigación de Rigobot se conserva como vía descartada para este objetivo.

## 6.2 Conversación cronológica recuperable

El transcript íntegro de la fase no está disponible después de la compactación. A continuación se incluyen literalmente los prompts de Lourdes que quedaron preservados, con las respuestas y acciones de C3PO resumidas solo cuando el texto no se retuvo completo. No se reconstruyen intercambios ausentes ni se incluyen comentarios particulares o datos personales.

### Solicitud inicial y exploración de CodeRevision

**Lourdes:** «Y por ultimo, vamos a por otra skill.
- titulo: **Consultar feedback de mis proyectos**
- objetivo: recuperar y organizar los comentarios, valoraciones y observaciones de los profesores sobre mis proyectos para ayudarme a entender qué he hecho bien y qué aspectos necesito mejorar.

Para ello:
- Investiga en la documentación de la API qué endpoints permiten obtener el feedback de mis proyectos, qué parámetros necesitan y qué información devuelven.
- Explícame qué datos podemos recuperar realmente: comentarios, puntuaciones, estado de revisión, recomendaciones y fechas de evaluación, si están disponibles.
- Propón cómo podría funcionar la skill, pero no crees ni modifiques archivos todavía.
- No amplíes la allowlist de la capa común sin consultarme; primero presenta los hallazgos y las opciones.»

**C3PO (investigación resumida):** revisó la skill de proyectos, la referencia local, allowlist, código público del API y documentación encontrada. Identificó CodeRevision y advirtió que no se había confirmado que su respuesta fuera la evaluación docente. No modificó archivos en esa etapa.

**Lourdes:** «Perfecto, investiga primero la ruta personal de revisión de código para comprobar si realmente podemos recuperar el feedback de los profesores.
Dime qué modificación concreta necesitarías en la allowlist de la capa común para realizar una consulta GET de prueba, qué requisitos previos tiene y qué medidas de seguridad mantendrías.
Quiero comprobar si podemos recuperar comentarios, observaciones y valoraciones reales de mis proyectos.
No utilices rutas de academia, no realices operaciones de escritura y no modifiques todavía la allowlist ni ningún otro archivo.
Primero explícame qué cambios necesitarías y espera mi aprobación.»

**C3PO:** explicó que la propuesta sería una ruta personal con ID numérico, los requisitos (proyecto propio, repo GitHub, cuenta GitHub conectada y posible restricción del servicio), y salvaguardas GET-only, TLS, sin redirecciones, errores suprimidos y datos mínimos. No cambió archivos ni consultó la ruta antes de recibir autorización.

**Lourdes:** «La propuesta me parece correcta.
Si es una consulta exclusivamente de lectura, sin efectos adicionales, podemos añadir únicamente esa ruta numérica y personal a la allowlist y realizar la prueba con uno de mis proyectos.
Mantén todas las medidas de seguridad que has descrito. No modifiques todavía ningún archivo.»

**Lourdes:** «De acuerdo, continúa.
Añade únicamente la ruta personal y numérica de revisión a la allowlist y realiza una consulta GET de prueba con uno de mis proyectos.
Mantén las medidas de seguridad acordadas. No modifiques la autenticación ni añadas otras rutas.
Después, muéstrame qué información has podido recuperar y qué campos reales devuelve la API.»

**C3PO (acciones/resultados registrados):** inspeccionó la allowlist y el predicado del cliente. Añadió al cliente de ejecución solo el patrón numérico personal `/v1/assignment/me/task/{task_id}/coderevision`; probó que se rechazaran IDs no numéricos, rutas de academia y segmentos extra. Una primera tarea sin `github_url` dio HTTP 404; luego una tarea con repositorio presente también devolvió HTTP 404. En ambos casos el cliente suprimió cuerpos. Se informó que no se recuperaron campos reales de revisión.

### Cambio de objetivo: evaluación docente en tareas 4Geeks

**Lourdes:** «cambiemos el enfoque. No nos interesa el feedback de Rigobot. Quiero recuperar es la evaluación que realizan los profesores cuando corrigen mis proyectos en 4Geeks.
Investiga dónde almacena la plataforma esas evaluaciones y qué endpoints permiten consultar los comentarios, observaciones, valoraciones y resultados que dejan los profesores.
Comprueba qué información devuelve la API, qué permisos necesita y si podemos acceder a ella mediante nuestra capa común.
No amplíes la allowlist ni modifiques archivos todavía. Primero explícame qué has encontrado.»

**C3PO (investigación resumida):** inspeccionó el código público de `BreatheCo-de/apiv2`, en particular rutas, vistas, serializadores y pruebas de Assignments. Encontró el detalle personal `GET /v1/assignment/task/{task_id}` y campos `description`, `revision_status`, `reviewed_at`; la ruta ya estaba permitida. La vista personal limita el resultado a la tarea del usuario autenticado. Las vistas de academia exigen capacidad `read_assignment`, pero no son necesarias. Explicó que no había evidencia de una puntuación numérica independiente.

**Lourdes:** «Perfecto. Vamos a comprobar esta vía con un proyecto que ya haya sido revisado.
Realiza una consulta GET de solo lectura al endpoint utilizando el ID de uno de mis proyectos aprobados y la capa común existente.
Quiero comprobar qué información contiene, y si description corresponde al feedback del profesor o a la descripción original de la tarea.
No muestres datos personales, no modifiques archivos ni amplíes la allowlist.»

**C3PO (consulta real resumida):** obtuvo un proyecto aprobado de la lista personal y consultó el detalle por la capa común. La respuesta contenía campos del serializador de tarea, incluidos `description`, `revision_status` y `reviewed_at`. `description` era un comentario breve distinto del título y del slug; eso confirmó su función como comentario de corrección en ese registro. La fecha de revisión estaba presente. No se mostraron datos personales.

### Definición y creación de skill

**Lourdes:** «Perfecto. Continúa con el análisis y la definición de la skill «Consultar feedback de mis proyectos», teniendo en cuenta lo que hemos comprobado.»

**C3PO (borrador de comportamiento):** propuso listar proyectos personales paginados y consultar cada detalle; mostrar título, estados, comentario de `description` y `reviewed_at`; no inventar puntuaciones ni recomendaciones; omitir datos personales; marcar listados incompletos y continuar tras fallos individuales. No creó archivos todavía.

**Lourdes:** «estas autorizado»

**C3PO (implementación):** creó `skills/consultar-feedback-proyectos/SKILL.md`, con llamadas solo por el cliente común, exclusión de Rigobot y rutas de academia, campos confirmados, no inferencia, gestión de errores y privacidad. La validación del skill creator devolvió «Skill is valid!». No creó helper/tests propios ni amplió allowlist para esta skill.

### Prueba end-to-end live

**Lourdes:** «Ejecuta la skill contra la API real para comprobar que funciona correctamente.
Verifica que recupera todos mis proyectos, consulta sus detalles y presenta correctamente los comentarios, estados de revisión y fechas disponibles.
Comprueba también el tratamiento de proyectos sin feedback y de errores de consulta.
No inventes valoraciones ni recomendaciones. No muestres datos personales.»

**C3PO (resultado live resumido):** el listado paginado recuperó 22 proyectos; todos los IDs eran numéricos. Se consultaron detalles de los 22 mediante el lanzador común, con 22 éxitos y 0 errores. El resumen agregado fue 15 `APPROVED`, 7 `PENDING`, 0 `REJECTED`; los aprobados tenían feedback textual y `reviewed_at`, y los pendientes carecían de `description` y `reviewed_at`. No se reprodujeron los comentarios particulares. Se comprobó el aislamiento/continuación de errores en el flujo documentado, pero no ocurrió un fallo real en las 22 peticiones live; por eso no se afirma que un fallo de servidor se haya observado live. No se presentaron IDs ni datos personales.

**Límites de recuperación.** El prompt inicial contiene un fragmento truncado tras la mención de recomendaciones/fechas en el resumen original; la bitácora conserva aquí el texto legible que quedó en las páginas recuperadas. Algunas respuestas intermedias de C3PO solo están disponibles como resúmenes del historial compacto. No se reconstruyen palabras ausentes. Ningún comentario individual, ID personal, email, campo `user` ni URL privada se copia en la bitácora.
