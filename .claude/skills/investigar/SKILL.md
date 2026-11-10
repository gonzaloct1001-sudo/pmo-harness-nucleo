---
name: investigar
description: Investigación auditable (arquetipo investigacion): encuadre, mapa de fuentes, hipótesis asesinas, expediente con marcas H/D/T/P, refutador, árbitro, ocho pruebas y entregable, con puertas que firma quien decide; también auditar un informe que afirma hechos. Úsala cuando el resultado dependa de hechos del mundo con fuente: «investiga…», «¿a quién le ofrecemos…?», «estado del arte», «due diligence», «¿es cierto que…?», «firmo P2».
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/trabajo.md`, `reglas/datos.md`, `reglas/entregables.md`, `reglas/confidencialidad.md`, `reglas/nucleo.md`.

# Investigar (protocolo de investigación auditable)

**Objetivo:** que un tercero hostil, con solo el entregable y su expediente, pueda reconstruir cómo se llegó a cada
afirmación y señalar dónde se rompería. El protocolo está en `arquetipos/investigacion/protocolo/` (léelo completo
la primera vez en la sesión: son cuatro archivos cortos). Los roles, en `references/roles/`.

**Tu guía en cada momento es el validador:** `python herramientas/investigacion.py <proyecto>` dice en qué etapa va
cada investigación, qué falta, qué leer y qué pedirle a la persona. Ejecútalo al empezar y después de cada paso.

## 0. Detectar y ubicar (siempre primero)
- **¿Es una investigación?** Sí, si para responder hay que afirmar hechos del mundo de afuera (terceros, registros,
  mercado, normativa, tecnología) que sostendrán una decisión o un entregable. Si la respuesta sale de un modelo con
  supuestos propios, es `estudio`; si hay de ambos, se combinan.
- **¿Hay una abierta?** El estado de inicio lista las investigaciones abiertas. Si el pedido calza con una, sigue
  esa (paso 2).
- **¿Dónde va?** Dilo en una línea y sigue, salvo que no sea evidente:
  - **Integrada:** alimenta otro trabajo del proyecto (por ejemplo, la sección de mercado o de propiedad intelectual
    de una postulación) → se abre dentro de ese proyecto.
  - **Proyecto propio:** la investigación es el producto → `nuevo-proyecto` con el arquetipo `investigacion` (o
    directamente `crear_proyecto.py <slug> --arquetipos investigacion`).
  - **Aislada:** es de otro cliente o requiere confidencialidad total → otra carpeta de empresa (`nueva_empresa.py`).
- Si la pregunta mezcla universos distintos (un «o» que separa mercados, poblaciones o productos), son dos
  investigaciones: se abren por separado y ninguna lee a la otra.

## 1. Abrir
`python herramientas/investigacion.py proyectos/<slug> --nueva <nombre-corto> [--cartucho biblioteca/dominios/<x>.md]`
- Toma la intensidad, la tolerancia y el cartucho por defecto de `empresa/investigacion/ajustes.yaml` (si no existe,
  lo crea). Si el proyecto no tenía el arquetipo, lo suma sin tocar lo demás.
- Se empieza en **sondeo** salvo que la persona pida otra cosa; se sube con `--subir estandar` cuando la decisión lo
  justifica (lo decide la persona).
- Si hay un cartucho en `biblioteca/dominios/` que calce con el dominio, úsalo. Si no hay y el dominio se repetirá,
  ofrece crear uno al cerrar.
- **Material que la persona ya tiene** (artículos, informes, fichas de proveedores, correos): dile que lo copie a
  `proyectos/<slug>/_entrada/` sin ordenar, e inventaríalo con `extraer_entrada.py` (o con `nuevo-proyecto` si además
  define el proyecto). Cada documento entra a `E1_mapa_fuentes.csv` con su nivel N1-N6 (`protocolo/marcas-y-fuentes.md`)
  y lo que afirma entra al expediente como T (testimonio) o P (pista), nunca como H, hasta que una fuente lo sostenga.

## 2. Avanzar por etapas (el ciclo)
Para cada paso:
1. `investigacion.py <proyecto> --instancia <id>` → etapa, rol, qué leer y qué falta.
2. Aplica **el rol de esa etapa** con su ficha (`references/roles/<rol>.md`), leyendo solo lo que la ficha indica:
   - E0 encuadrador · E1 cartógrafo · E2 refutador (escribe las hipótesis) y bibliotecario (las corre) ·
     E3–E4 analista (con el bibliotecario si faltan hechos) · E5 refutador (pase 2) y árbitro · E6 editor.
   - En Claude Code, **bibliotecario, refutador y árbitro corren como subagentes** (`.claude/agents/`), con la ruta
     de la investigación y la lista exacta de archivos que pueden leer. El refutador del pase 2 recibe solo
     `conclusiones.csv` y `expediente.csv`, nunca el análisis. Si `ajustes.yaml` define `refutador.modelo`, invoca
     refutador y árbitro con ese modelo; si define `refutador.asistente`, pide a la persona que corra el pase 2 en ese
     asistente (le das la instrucción lista para pegar).
   - Sin subagentes: cada rol en un paso separado (regla de AGENTS.md).
3. `investigacion.py <proyecto> --instancia <id> --revisar`. Si hay errores, primero
   `--corregir` (vista previa) y `--corregir --aplicar`: arregla lo mecánico (valores mal escritos, H con fuente N4 →
   T, H con fuente N5–N6 → P, «no consultado» en la bitácora → vacío no-buscado) y lo deja anotado en cada fila. Lo
   que requiere juicio vuelve al rol que corresponde. No avances con errores.
4. Puerta:
   - **P1, P3, P4 (árbitro):** el subagente árbitro la revisa y firma, o devuelve el trabajo con el motivo.
   - **P0, P2, P5 (persona):** nunca las firmas tú. Pide la firma en **dos líneas, con la frase exacta**:
     > «Ninguna de las 5 hipótesis asesinas disparó (detalle abajo). Responde **firmo P2** o dime qué corregir.»

     Debajo, plegado o en viñetas, lo que necesita para decidir (máximo 6 líneas). Con su respuesta, anota en
     `puertas.csv`: `aprobada`, su nombre, `persona` y la fecha. Si corrige algo, se corrige y se vuelve a pedir.
   - Si una hipótesis **disparó**: pregúntale si reencuadrar (vuelve a E0; P0 se firma de nuevo) o cerrar. Es el
     momento más barato para detenerse; dilo así.
5. Actualiza el traspaso del proyecto (`seguimiento/traspaso.md`): investigación, etapa y próximo paso.

## 3. Reglas de conversación (pensadas para quien no conoce el protocolo)
- Habla en simple: «la pregunta», «lo que tiene que ser cierto», «lo que encontró el refutador». Las siglas (H, P2,
  N1) van entre paréntesis, no como explicación.
- Una decisión por vez, con la respuesta exacta para darla. Nunca le pidas que edite archivos.
- Nunca firmes por la persona, nunca saltes una puerta y nunca defiendas una conclusión tumbada: se retira.
- Si la persona dice «eso ya está resuelto» sobre una hipótesis asesina, se anota como testimonio (T) y se busca la
  evidencia: la hipótesis no se cierra con su palabra (explícale por qué en una línea).

## 4. Aprender y ajustar (lo propio de cada empresa)
- **Cuando la persona corrige algo de método** («busca también en portugués», «para esto usa siempre el registro
  X», «no me sirven los sondeos, parte en estándar»): pregúntale en una línea si vale **de ahora en adelante**. Si sí:
  - preferencia → `investigacion.py --preferencia "<texto>" --quien "<nombre>" --desde <proyecto>/<id>`;
  - valor por defecto o regla → `investigacion.py --ajustar <clave>=<valor> --quien "<nombre>" --motivo "<por qué>"`
    (claves: `por_defecto.intensidad`, `por_defecto.tolerancia`, `por_defecto.restriccion_fuentes`,
    `por_defecto.cartucho`, `reglas.antiguedad_max_anios`, `reglas.minimo_hipotesis`, `reglas.muestra_trazabilidad`,
    `refutador.asistente`, `refutador.modelo`). El validador no deja bajar las reglas bajo el mínimo del protocolo.
- **Cuando algo falla por una razón que se puede repetir** (una puerta rechazada, una conclusión tumbada por la misma
  causa, un error que el validador corrigió varias veces): anótalo en `metodo.csv` de la investigación (solo método,
  nunca hechos del caso).
- **Al cerrar:** `investigacion.py <proyecto> --instancia <id> --aprender` lista las lecciones; muéstraselas y, con su
  sí, `--aprender --llevar M-01,M-02 --quien "<nombre>"` las lleva a `empresa/investigacion/lecciones.csv`. Las
  investigaciones siguientes las leen (el validador las anuncia en «Leer»). Si una lección vale para cualquier
  empresa, agrega `--al-nucleo`; `--exportar-lecciones` las prepara para enviarlas a quien mantiene el núcleo.
- Todo esto vive en `empresa/investigacion/`, que **ninguna actualización del núcleo toca**.

## 5. Cerrar
1. El editor arma `E6_entregable.md`; `--revisar` sin errores; se anota `cierre` en el manifiesto.
2. Si se pide el documento: `reportes` con `informe-investigacion` y `verificar_autoria.py` en OK.
3. Si es integrada: la sección que alimenta cita las conclusiones (C-xx) o hechos (E-xx) de la investigación; nada
   que no esté arbitrado pasa a la postulación o al estudio.
4. Paso 4 (aprender) y `guardar-cambios`.

## 6. Auditar un documento existente
Para un informe, estudio o sección que ya afirma hechos («¿esto se sostiene?»), sin abrir una investigación
completa: lista sus afirmaciones portantes, marca cada una (H, D, T, P, I, S, V) según su fuente real y aplica las
ocho pruebas de `protocolo/auditoria.md`. Deja el resultado en el proyecto (por ejemplo `estudio/revision_<fecha>.md`)
con: afirmaciones sin anclaje N1–N3, testimonios leídos como hechos, fuentes de un solo origen y qué buscar para
cerrarlas. Si la persona quiere cerrarlas, abre una investigación (sondeo) con esa pregunta.

## Criterios de calidad
- Ninguna afirmación del entregable sin marca y cita; ninguna conclusión portante sin «se revierte si».
- La bitácora tiene búsquedas nulas; lo no buscado está en vacíos, no en la bitácora.
- Las puertas están firmadas en orden, y las de la persona, por la persona.
- `--revisar` en OK antes de pedir una firma y antes de cerrar.
