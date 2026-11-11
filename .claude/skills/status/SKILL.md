---
name: status
description: Status de todos los proyectos: semáforos, lo que vence, decisiones y avance; agenda del día (lo vencido, lo de hoy, lo que viene); reporte web semanal agendable y tablero único de varias empresas. Úsala con «¿cómo vamos?», «dame el status», «¿qué tengo pendiente hoy?», «agéndalo los lunes a las 9», «quiero ver todas mis empresas juntas».
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/trabajo.md`, `reglas/datos.md`, `reglas/entregables.md`, `reglas/organizacion.md`.

# Status

Herramienta: `python herramientas/status.py` (solo lee; usa los mismos cálculos de cada proyecto). Las reglas del
semáforo están en su encabezado: explícalas si el usuario pregunta por qué algo está en rojo o amarillo.

## 1. En el chat (a diario)
1. `python herramientas/status.py` (con `--hoy AAAA-MM-DD` si el usuario pide otra fecha de corte).
2. Responde breve, de lo urgente a lo informativo:
   - los rojos y amarillos con su motivo, y **qué hacer** con cada uno (una acción concreta);
   - lo que vence en los próximos 7 a 14 días;
   - lo que **requiere su decisión**;
   - lo que cambió desde el status anterior, si hay.
   Los verdes van en una sola línea. No pegues la tabla completa salvo que la pida.
3. **Al iniciar la sesión** el estado ya trae el status breve: muéstralo en 2 a 4 líneas junto al saludo.
4. **Agenda del día** («¿qué tengo pendiente?», «la minuta de pendientes», «¿qué vence esta semana?»):
   `python herramientas/agenda.py [--dias 14]`. Lista lo vencido, lo de hoy, lo que viene y los reportes que tocan
   hoy, de todos los proyectos; no muestra lo de un proyecto con `proyecto.estado: pausado`. Muéstrala tal cual, lo
   vencido primero, y no actúes sobre ella sin que lo pida. En Claude Code llega sola en la primera interacción del
   día (hook `agenda_diaria.py`); en otra herramienta, ejecútala con `--una-vez` al recibir el primer pedido del día.
   Para que un reporte aparezca el día que toca, su definición (`reportes/catalogo/<tipo>.md`) lleva `dia:` (un día
   de la semana, números del mes o `ultimo`): ofrécelo cuando el usuario diga «el informe sale los lunes».

## 2. Reporte web (cuando pide «reporte», «informe de status», «para el directorio», «para revisarlo»)
1. `python herramientas/status.py --formato html --abrir` → `status/status-AAAA-MM-DD.html`, que se abre en su
   navegador. Si lo quiere también en Excel o Markdown: `--formato html,xlsx` o `--formato md`. Para Word o PowerPoint
   con su formato, usa `reportes` con el Markdown del status como fuente.
2. Luego pregunta: **«¿Quieres que te lo prepare automáticamente cada semana? ¿Qué día y a qué hora?»**
   - Si dice que sí, explica en una línea que se crea una tarea programada en este computador (se abre sola si el
     computador está encendido) y, con su confirmación:
     `python herramientas/agendar_status.py --dia <día> --hora <HH:MM>`.
   - Para verla o quitarla: `--ver` o `--quitar`. En otro computador se agenda de nuevo.

## 3. Varias empresas: ¿un tablero único o uno por empresa?
Cada carpeta de empresa ya tiene su propio status, en su carpeta y su repositorio. Si el usuario lleva más de una
empresa (o pide «todas mis empresas», «status general»), **pregúntale qué prefiere**: no lo supongas.
- **Por empresa** (separados): no hay nada que crear; en cada carpeta se pide su status.
- **Tablero único** (todas juntas en una vista):
  1. Explica la privacidad en simple: el tablero junta resúmenes de varias empresas, así que va en **una carpeta y un
     repositorio privado nuevos, solo para él**, independientes de los de cada empresa. Nunca se guarda dentro de la
     carpeta de una empresa.
  2. Propón la carpeta (por defecto, junto a las de las empresas: `Documentos/PMO-Empresas/Panel-<nombre>`) y ejecuta
     `python herramientas/status.py --crear-panel <carpeta> --empresas <carpeta1> <carpeta2> ... --nombre "<nombre>"`.
  3. Con su permiso, crea el repositorio privado: `gh repo create <nombre-carpeta> --private --source <carpeta> --push`
     y `gh repo edit --add-topic pmo-harness-panel` (si no hay `gh`, que cree en GitHub un repositorio **privado** vacío).
  4. Status del tablero: `python herramientas/status.py --panel <carpeta>` (chat) o con `--formato html --abrir`.
     Para agendarlo: `agendar_status.py --dia ... --hora ... --panel <carpeta>`.
- Si las empresas son parte de **una misma entidad** y prefiere llevarlas juntas en una sola carpeta (misma marca,
  mismo banco de antecedentes), eso se decide al crear sus carpetas: ver `instalar` («Otra empresa»).

## 4. Plazos que no son tareas
Si el usuario menciona un plazo con una entidad (por ejemplo, «el SSM vence el 31 de julio», una rendición, la
renovación de una garantía), regístralo, con su confirmación, en `seguimiento/vencimientos.csv` del proyecto
(`id,fecha,compromiso,tipo,responsable,estado,comentario`). Aparece en la agenda y pone el proyecto en amarillo una
semana antes y en rojo si vence.

## Qué no hacer
- No modificar datos para que el semáforo se vea mejor: el status refleja los registros; si algo está mal, se corrige
  el registro con la skill que corresponda.
- No copiar el status de una empresa a la carpeta o el repositorio de otra.
