# Ficha de diseño — Diario de aprendizaje diario

**Estado:** solo diseño. No implementaré la skill ni crearé documentos o conexiones durante esta fase.

## 1. Qué hace la skill

- Convierte los aprendizajes que Lourdes comparta —incluso en puntos breves o desordenados— en propuestas organizadas para su diario de conocimiento.
- Se activa cuando Lourdes la pide expresamente. También puede sugerirse si detecta aprendizajes relevantes de una clase, ejercicio o proyecto. No preparará ni guardará una entrada automáticamente: primero mostrará los puntos detectados y preguntará si Lourdes quiere incorporarlos.
- Organiza la información por tema, clase o proyecto; señala posibles duplicidades y datos importantes que falten.
- Antes de preparar entradas definitivas, muestra cómo propone distribuir los contenidos. Lourdes puede corregir, ampliar o descartar puntos. La skill espera su confirmación antes de seguir.
- Después de la confirmación, prepara la entrada completa para que Lourdes la revise. Solo la guarda con su aprobación expresa.
- Su objetivo es consolidar lo aprendido y dejar un registro fiel de lo que Lourdes ha aprendido y trabajado, sin inventar contenido ni completar lagunas por su cuenta.

## 2. Qué información necesita y puede consultar

### Fuentes permitidas

- Las conversaciones entre Lourdes y el asistente.
- Los apuntes de la academia que Lourdes comparta.
- Los ejemplos y explicaciones trabajados juntos que estén disponibles en el contexto, incluso entre sesiones cuando sea pertinente.

La skill no consulta fuentes externas para completar entradas, salvo que Lourdes lo pida expresamente. Si falta información esencial o algo no está claro, pregunta; no presenta suposiciones como hechos.

### Datos necesarios para identificar y organizar una entrada

- **Tema o módulo.**
- **Fecha de clase**, en formato día/mes/año.
- **Aprendizajes o contenidos trabajados**, aunque estén expresados como notas breves.

Si alguno de estos datos no está claro, la skill pide la aclaración necesaria antes de organizar la entrada. No pregunta por cada campo que pueda quedar sin especificar.

### Datos que pueden quedar sin especificar

- **Fecha de registro:** se completa automáticamente con la fecha real del sistema cuando Lourdes confirma que quiere incorporar la entrada; no se le pregunta.
- **Fecha estipulada de realización:** si Lourdes no la ha indicado, la skill pregunta antes de completar la entrada. Si no recuerda la fecha, puede quedar como **«sin fecha»**.
- **Proyecto o ejercicio relacionado:** se incluye si lo hay; de lo contrario, puede indicarse que no aplica.
- **Ejemplos prácticos, dudas y conceptos por reforzar:** se incluyen cuando hay información disponible. Estos tres apartados aparecen siempre, aunque se indique que no hay contenido que añadir.

Las fechas usan el formato **día/mes/año**.

## 3. Qué resultado produce y dónde queda guardado

- Si Lourdes comparte aprendizajes de temas distintos, la skill propone entradas separadas. Si están relacionados y pertenecen al mismo tema o proyecto, puede agruparlos en una entrada.
- Antes de preparar las entradas definitivas, muestra cómo organizó los contenidos y espera la confirmación de Lourdes. Evita duplicidades y no mezcla aprendizajes sin relación.
- Cada entrada lleva el título: **Tema o módulo — Fecha de clase / Fecha de realización**. Si no se conoce esta última fecha, aparece **«sin fecha»**.
- La entrada incluye:
  - Fecha de clase.
  - Fecha de registro.
  - Fecha estipulada de realización.
  - Tema o módulo.
  - Proyecto o ejercicio relacionado, si lo hay.
  - Aprendizajes principales.
  - Ejemplos prácticos.
  - Dudas surgidas.
  - Conceptos por reforzar.
- Tras la confirmación de Lourdes, presenta la entrada completa para que la revise. No la guarda hasta recibir su aprobación expresa.
- El destino previsto es un **Google Doc**. Queda pendiente para la fase de implementación decidir si se usará un documento existente o se creará uno nuevo. Durante la fase de diseño no se hace ninguna conexión ni se crea ningún documento.

**Pendiente para implementación:** decidir el Google Doc de destino y autorizar por separado cualquier conexión o acción necesaria para guardar las entradas.

---

# Ficha de diseño — Plan semanal

**Estado:** propuesta para revisión. No implementaré la skill ni crearé documentos o eventos durante esta fase.

## 1. Qué hace la skill

### Objetivo y alcance

Ayuda a organizar y priorizar objetivos, tareas y compromisos semanales de cualquier ámbito que Lourdes necesite planificar, sin limitarse a categorías fijas. Puede abarcar, entre otros, el curso de AI Engineer, trabajo, tareas personales, gestiones, compromisos familiares y otros ámbitos que se incorporen en el futuro.

Propone un plan semanal realista, considerando importancia, urgencia, dependencias, fechas límite, disponibilidad y compromisos existentes. No intenta encajar todas las tareas si el tiempo no alcanza: señala la sobrecarga, sugiere qué tareas convendría aplazar y explica brevemente por qué. Espera la confirmación de Lourdes antes de cambiar prioridades o el plan.

### Cuándo se utiliza

- Lourdes puede pedir un plan cuando lo necesite.
- Como automatización propuesta, los domingos a las **21:00, hora peninsular de España (`Europe/Madrid`)**, la skill preguntará si quiere preparar el plan de la semana siguiente. La hora deberá respetar los cambios de horario de verano e invierno.
- La pregunta del domingo no inicia el proceso: la skill espera la confirmación de Lourdes. Si pospone el aviso, podrá elegir otro día u hora para preparar el plan. Si decide no preparar el plan esa semana, se omite esa vez y la pregunta habitual vuelve el domingo siguiente.
- La semana de planificación va de **lunes a domingo**, aunque la invitación a prepararla se envíe el domingo anterior.
- Si comparte un objetivo amplio sin tareas concretas, la skill puede sugerir pasos posibles. Debe distinguir claramente esos pasos de las tareas indicadas por Lourdes y esperar su confirmación antes de incorporarlos al plan; no presumirá que son necesarios.

### Revisión de planes anteriores y tareas pendientes

Al empezar un plan nuevo, la skill revisa la información de planes anteriores disponible y le pregunta a Lourdes qué tareas se completaron, cuáles siguen pendientes y cuáles cambiaron. También identifica las que quedaron a medias. No cambia el estado de ninguna tarea sin confirmación.

Las tareas pendientes no pasan automáticamente al nuevo plan. Se vuelven a valorar para decidir si se incluyen esa semana, quedan pendientes fuera del plan o dejan de ser necesarias. La valoración se hace junto con los nuevos objetivos y compromisos.

Cuando todas las tareas de un plan estén confirmadas como completadas, ese plan se considera completo y cerrado, y no se revisa automáticamente al preparar planes posteriores.

**Planes cerrados e histórico:** Los planes cerrados se conservan en Google Drive como parte del histórico y Lourdes puede consultarlos cuando lo solicite. Dejan de revisarse automáticamente al preparar planes nuevos y no se modifican. Cada consulta a Google Drive requiere autorización puntual; consultar un plan cerrado no autoriza a cambiarlo.

Si la carga semanal parece superar el tiempo disponible, la skill indica el problema y sugiere qué tareas convendría aplazar, con una breve razón. Espera confirmación antes de modificar prioridades o el plan. Las tareas que se decida dejar fuera se muestran en **«Pendiente para otra semana»**, con el motivo, para revisarlas al preparar el siguiente plan.

### Revisión durante la semana

Lourdes puede pedir una revisión del plan en cualquier momento de la semana ante cambios, nuevas tareas o imprevistos. La skill revisa el plan vigente, considera la nueva información y propone los ajustes necesarios. Muestra los cambios y espera autorización antes de actualizar el documento de Google Docs. Esta autorización no permite modificar eventos de Google Calendar: cada acción en Calendar requiere autorización expresa aparte.

### Criterios para decidir prioridades y resolver conflictos

Si hay objetivos o tareas en conflicto, la skill muestra el conflicto en el resumen previo al plan, detallando:

- Qué plazos, compromisos o prioridades son incompatibles.
- Las opciones posibles para resolverlo.
- Una recomendación, con una justificación breve.

Después espera la confirmación de Lourdes antes de cambiar prioridades, aplazar tareas o modificar compromisos. No toma esas decisiones por ella.

## 2. Qué información necesita

### Información que Lourdes puede proporcionar

Lourdes puede compartir objetivos, tareas pendientes, fechas límite, prioridades, compromisos y disponibilidad en el formato que le resulte cómodo, incluso en una lista desordenada o en mensajes separados. La descripción de qué hay que hacer es el mínimo necesario para identificar una tarea. El ámbito y el plazo son importantes, pero solo se pedirán si hacen falta para planificarla correctamente; la falta de un dato opcional no impide incluir una tarea.

Para la disponibilidad, la skill comprueba primero qué información actualizada ya tiene. No presupone que se repita de una semana a otra. Pregunta solo por cambios o datos que falten, incluidas las franjas disponibles y las que Lourdes quiera reservar para descansar. Respeta los compromisos fijos que ya se conozcan o que se hayan podido consultar en Calendar con autorización.

Si un dato de una tarea no está disponible, no lo inventa ni pregunta automáticamente por todos los campos: lo deja sin especificar, salvo que sea imprescindible para organizar el plan.

### Consulta y revisión antes de planificar

Antes de elaborar el plan, la skill organiza y agrupa la información y presenta a Lourdes un resumen para que lo revise y corrija. El resumen incluirá:

- Objetivos de la semana.
- Tareas nuevas y pendientes de semanas anteriores.
- Compromisos fijos y recurrentes.
- Disponibilidad y franjas reservadas para descanso.
- Festivos de esa semana.
- Fechas límite y prioridades conocidas.
- Información que falte o necesite confirmación.
- Conflictos detectados, con las opciones posibles y una recomendación breve.

La skill espera la corrección o confirmación de Lourdes antes de continuar con el plan.

### Fuentes externas y autorización

La skill puede trabajar con lo que Lourdes indique y con fuentes externas que autorice, por ejemplo:

- **Google Calendar**, para consultar clases, citas, compromisos fijos o recurrentes y festivos que aparezcan en el calendario.
- **Google Drive**, para consultar documentos con planes anteriores o listas de tareas en la carpeta específica que se decida durante la implementación.
- La información del curso y sus actividades se la proporcionará Lourdes. La skill no pedirá acceso a la plataforma de la academia.

Cada vez que la skill necesite consultar Google Calendar o Google Drive, pedirá autorización para esa consulta concreta. La autorización será puntual y no se conservará para planes futuros.

Si Lourdes no autoriza una consulta, la skill sigue trabajando con la información que le haya proporcionado e indica qué datos no pudo verificar. Solo pregunta si esa falta impide crear un plan coherente y realista; los datos opcionales no bloquean la planificación.

Si al consultar Calendar la skill detecta un festivo en la semana, pregunta a Lourdes cómo organizar ese día. No asume que sea libre ni que deba estudiar.

## 3. Qué resultado produce

### Plan semanal

Cada plan se prepara como borrador para que Lourdes lo revise, corrija y apruebe antes de guardarlo. El documento deberá tener un título con este formato, usando las fechas del lunes y el domingo correspondientes:

**Plan semanal — DD/MM/AAAA al DD/MM/AAAA**

El contenido se organiza en este orden:

1. **Resumen de los objetivos principales de la semana.**
2. **Visión general de la carga de trabajo.**
3. **Plan organizado por días.**
4. **«Pendiente para otra semana»**, con las tareas que se hayan decidido no incluir y el motivo.

El plan diario diferencia claramente:

- **Compromisos fijos:** aparecen en el día y la franja horaria correspondientes. La skill respeta los horarios indicados por Lourdes o consultados en Google Calendar con autorización, e incluye los compromisos recurrentes conocidos.
- **Tareas flexibles:** se distribuyen según prioridad, duración, disponibilidad y fecha límite. La skill puede recomendar días o momentos, pero no les asigna horarios rígidos.

El plan permite visualizar la carga de cada día sin perder flexibilidad para imprevistos. No impone un límite diario rígido, salvo que Lourdes lo indique expresamente. Reparte la carga de forma realista, evita sobrecargar determinados días y deja margen para descansos e imprevistos. Si la carga no es asumible en el tiempo disponible, advierte a Lourdes y propone reajustes para que ella decida.

Cuando se conozcan, para cada tarea incluye:

- **Prioridad:** alta, media o baja.
- **Duración:** especifica si la proporcionó Lourdes o si es una estimación de la skill.
- **Fecha límite:** la fecha correspondiente o **«sin fecha»**.
- **Tareas previas:** las tareas o condiciones necesarias antes de realizarla, o **«no hay»**.

Las duraciones u horarios que proporcione Lourdes se usan como referencia. Si falta una duración, la skill puede estimarla, identificarla claramente como estimación y preguntar si hay dudas importantes que puedan cambiar la planificación. No pregunta por todos los campos opcionales.

### Documento y archivo

Cada plan semanal se guarda en un **Google Doc nuevo**, para conservar un histórico organizado. No se modifican ni sobrescriben documentos de semanas anteriores.

Antes de crear el documento, la skill presenta el plan completo como borrador. Solo lo crea y guarda después de recibir la autorización expresa de Lourdes. Los planes se guardan y consultan en una carpeta específica de Google Drive; su nombre y ubicación se decidirán durante la implementación. Cada consulta de Drive requiere autorización puntual.

### Propuestas de eventos para Google Calendar

El plan puede incluir propuestas para añadir a Google Calendar:

- Compromisos con fecha y hora definidas.
- Recordatorios para tareas flexibles cuando resulte útil.

Una vez aprobado el plan, la skill muestra las propuestas de eventos y espera autorización expresa para crear **cada evento por separado**. Aprobar el plan no autoriza la creación de eventos. Tampoco modifica ni elimina eventos existentes sin autorización expresa. La revisión o actualización del plan en Google Docs tampoco autoriza cambios en Calendar.

## Pendientes para una eventual implementación

- Definir el nombre y la ubicación de la carpeta específica de Google Drive.
- Determinar y autorizar cómo se configuraría el aviso semanal de los domingos a las 21:00, hora `Europe/Madrid`, incluidas las opciones de posponer u omitir una semana.

**No se ha programado el aviso, ni se han creado documentos, carpetas o eventos.**
