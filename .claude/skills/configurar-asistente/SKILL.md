---
name: configurar-asistente
description: Deja a un asistente de IA (Claude Code, OpenAI Codex, Gemini, Cursor, GitHub Copilot u otro) listo para operar el harness igual que los demás — identifica la herramienta, revisa qué archivo de instrucciones lee, crea solo la puerta de entrada que falte (siempre remitiendo a AGENTS.md), activa los controles de Git, prueba que todo funcione y lo registra; y, si se cambia de asistente a mitad de un trabajo, retoma desde el traspaso. Úsala cuando el estado de inicio diga que el asistente no está registrado, cuando el usuario empiece a usar otra IA o cambie de una a otra, o pregunte si puede usar el harness con otra IA.
---

# Configurar asistente

**Meta:** que cualquier asistente opere con las mismas reglas, procedimientos y controles, sin duplicar
instrucciones. La fuente única de reglas es `AGENTS.md`: las demás puertas de entrada solo la importan o remiten a
ella. Habla en simple; esto debe tomar un par de minutos.

## 1. Identificar el asistente
1. Determina qué herramienta eres (la aplicación o extensión, no solo el modelo). Si no estás seguro (por ejemplo,
   una extensión que permite elegir entre varios modelos), pregúntalo en una línea.
2. Búscala en `references/asistentes.md`. Usa su `id` en todo lo que sigue.

## 2. Revisar la puerta de entrada
- **Herramienta conocida:** verifica que exista el archivo que lee al iniciar (columna «Lee al iniciar»). Si falta,
  créalo con la plantilla de abajo.
- **Herramienta desconocida:**
  1. Averigua, con tu propio conocimiento de la herramienta, su documentación o preguntando al usuario:
     qué archivo de instrucciones del proyecto lee al iniciar, si ejecuta comandos en la consola, si soporta
     procedimientos (skills), hooks y subagentes, y cómo pide permiso para los comandos.
  2. Si **no puede leer archivos de la carpeta ni ejecutar comandos** (un chat en el navegador, por ejemplo),
     explícale al usuario que no puede operar el harness y sugiérele una de la tabla. No sigas.
  3. Crea **solo** el archivo de entrada que esa herramienta lee, con la plantilla de abajo. Si la herramienta ya lee
     `AGENTS.md`, no crees nada.
  4. Agrégala a `.harness/asistentes.yaml` con `origen: configurado-en-sesion` y sugiere al usuario avisar a quien
     mantiene el núcleo para sumarla a `references/asistentes.md` (aquí no la agregues: es del núcleo y se
     reemplaza al actualizarlo).
- **Nunca copies las reglas de `AGENTS.md` a otro archivo:** dos copias se desincronizan. La puerta de entrada solo
  remite.

Plantilla de puerta de entrada (`<ARCHIVO>` es el que lee la herramienta):
```markdown
# PMO Harness — entrada para <Herramienta>

Las reglas de esta carpeta están en `AGENTS.md`, la fuente única para cualquier asistente de IA.
@AGENTS.md            ← deja esta línea solo si la herramienta permite importar archivos con @

Antes de responder cualquier cosa, lee `AGENTS.md` completo y sigue su paso 0 (ejecutar `python herramientas/estado.py --remoto`).
Tu id en `.harness/asistentes.yaml` es `<id>`. Los procedimientos están en `.claude/skills/<nombre>/SKILL.md`.
```

## 3. Controles
1. **Git (todas las herramientas):** si `git config --get core.hooksPath` no devuelve `.githooks`, actívalo con
   `git config core.hooksPath .githooks` (se configura una vez por computador). En Mac, si Git avisa que el hook no
   es ejecutable: `chmod +x .githooks/pre-commit herramientas/*.sh`.
2. **Hooks propios de la herramienta**, si los tiene (ejecutar algo al iniciar la sesión, antes de un comando o
   después de editar): propón configurarlos para llamar a los mismos scripts —`herramientas/estado.py --remoto` al
   iniciar y `herramientas/hooks/precommit.py --archivos <ruta>` después de editar CSV o YAML—, explica qué archivo
   de configuración se modifica y **pide confirmación** antes de hacerlo.
3. **Sin hooks:** recuerda que el paso 0 de `AGENTS.md` y la validación después de editar (regla 16) los haces tú.
4. **Permisos:** recomienda que la herramienta pida confirmación para comandos que salgan de la carpeta o borren
   archivos. No desactives las confirmaciones sin que el usuario lo pida.

## 4. Prueba de humo (no modifica datos)
1. `python herramientas/estado.py` → debe mostrar `[Estado del PMO Harness]`.
2. Lee `.claude/skills/ayuda/SKILL.md` y resume en una línea qué hace (comprueba que puedes leer procedimientos).
3. `python herramientas/validar_proyecto.py ejemplos/demo-andes --hoy 2026-09-25` → debe terminar mostrando hallazgos
   (los errores están sembrados a propósito).
4. `git config --get core.hooksPath` → `.githooks`.
5. `python herramientas/hooks/precommit.py --archivos ejemplos/demo-andes/riesgos/riesgos.csv` → `OK`.
Si un paso falla, corrígelo o explica al usuario en simple qué falta (por ejemplo, instalar Python con `instalar`).

## 5. Registrar
Agrega o actualiza tu entrada en `.harness/asistentes.yaml` (créalo si no existe; si no existe `.harness/`, el
harness no está instalado: sigue con `instalar`, que lo crea):
```yaml
asistentes:
  - id: codex                      # id de references/asistentes.md, o uno nuevo en minúsculas
    nombre: OpenAI Codex
    archivo_entrada: AGENTS.md     # el que lee al iniciar
    procedimientos: lee SKILL.md   # nativos | lee SKILL.md
    controles: [git]               # [hooks-propios, git]
    subagentes: no                 # si | no (roles en pasos separados)
    origen: tabla                  # tabla | configurado-en-sesion
    configurado: 2026-10-19
    prueba_de_humo: ok             # ok | con observaciones
```
Termina con una línea al usuario: qué quedó configurado y que puede pedir lo mismo de siempre, con sus palabras.

## 6. Cambio de asistente a mitad de camino
Si el estado muestra traspasos de un asistente distinto, o trabajo sin guardar que no explica ningún traspaso:
1. Lee `seguimiento/traspaso.md` de cada proyecto con tarea en curso y, si hay un alta en curso,
   `_entrada/_procesado/avance-alta.md`.
2. El asistente anterior pudo cortarse antes de actualizar el traspaso (por ejemplo, porque se le acabó la cuota):
   revisa `git status` y `git diff` de los archivos modificados sin guardar para reconstruir en qué iba.
3. Resume al usuario en 3 líneas en qué quedó el trabajo, propón continuar desde el próximo paso y, al primer
   avance, actualiza el traspaso con tu `id`.
