# Arquetipo: Investigación auditable

## Cuándo usarlo
Cuando el producto es **una respuesta que depende de hechos del mundo de afuera que hay que verificar con fuentes**,
y un error en esos hechos tiene costo: a quién ofrecer una licencia o una alianza, qué proveedores o socios califican,
quiénes son los competidores reales, el estado del arte o de la técnica, la libertad de operación frente a patentes,
la situación de una contraparte (due diligence), qué exige una norma, si una afirmación de un tercero es cierta.

Sirve en cualquier área: lo que cambia de un rubro a otro va en un **cartucho de dominio**
(`biblioteca/dominios/`), no en el protocolo.

Señales para reconocerla (en la descripción del usuario o en los documentos de `_entrada/`):
- verbos como investigar, averiguar, mapear, identificar candidatos, levantar antecedentes, verificar, vigilar;
- preguntas sobre terceros («¿quién puede…?», «¿a quién le ofrecemos…?», «¿es cierto que…?»);
- una postulación o estudio con secciones de mercado, competencia, estado del arte, propiedad intelectual o
  contrapartes que hoy se escriben «de memoria»;
- registros, patentes, ensayos, licitaciones adjudicadas o normas como fuente de la respuesta.

No es lo mismo que `estudio`: el estudio recomienda a partir de un modelo y sus supuestos (VAN, escenarios); la
investigación establece qué es cierto afuera. Se combinan cuando un estudio necesita hechos verificados.

## Tres formas de usarlo (las elige quien trabaja)
| Forma | Cuándo | Cómo |
| --- | --- | --- |
| Integrada | La investigación alimenta otro trabajo del proyecto (p. ej., la sección de mercado o de propiedad intelectual de una postulación) | Se abre dentro de ese proyecto (`investigacion.py <proyecto> --nueva …` suma el arquetipo solo); lo que pasa al otro trabajo cita las conclusiones (C-xx) |
| Proyecto propio | La investigación es el producto | `crear_proyecto.py <slug> --arquetipos investigacion`; puede tener varias investigaciones |
| Aislada | Otro cliente, o confidencialidad total | Otra carpeta de empresa (`nueva_empresa.py`), con su repositorio privado |

En todas, cada investigación vive en `investigaciones/<AAAA-NN-nombre>/` y es aislada: tiene su propio expediente y
no usa hechos de otra (si los necesita, los reingresa con su fuente y fecha). El validador lo controla.

## Cómo funciona (en simple)
1. **Encuadre (E0):** se escribe qué decisión se tomará con el resultado, y su contrario. La persona que decide firma
   (P0). No se busca nada antes.
2. **Mapa de fuentes (E1):** dónde están los registros que prueban cosas en ese dominio.
3. **Hipótesis asesinas (E2):** lo que tiene que ser cierto para que valga la pena seguir; se buscan antes de
   construir nada. Si una dispara, se reencuadra o se cierra. La persona firma (P2).
4. **Universo y análisis (E3–E4):** candidatos con señal y fuente; argumento y conclusiones citando el expediente.
5. **Contrastación (E5):** un refutador que no vio el razonamiento intenta tumbar cada conclusión; un árbitro aplica
   las reglas y las ocho pruebas. La persona firma (P5).
6. **Entregable (E6):** la respuesta primero, cada afirmación con su marca y fuente, lo que no se sabe y el límite de
   cobertura.

El detalle está en `protocolo/` (`PROTOCOLO.md`, `marcas-y-fuentes.md`, `puertas.md`, `auditoria.md`).

## Qué agrega a la base
- `investigaciones/` con una carpeta por investigación (se crea con `investigacion.py --nueva`, desde
  `arquetipos/investigacion/plantilla-instancia/`): manifiesto, archivos E0 a E6, expediente, bitácora, vacíos,
  puertas, conclusiones, impugnaciones, auditoría y método.
- Reporte `informe-investigacion` (Word desde el entregable).
- En la empresa: `empresa/investigacion/ajustes.yaml` (valores por defecto, reglas, refutador, preferencias) y
  `lecciones.csv` (lo aprendido), que ninguna actualización del núcleo toca.

## Herramientas
- `python herramientas/investigacion.py <proyecto>`: dónde va cada investigación y el siguiente paso.
- `--nueva <nombre-corto>` abre una; `--revisar` valida; `--corregir [--aplicar]` arregla lo mecánico; `--auditar` y
  `--muestra` hacen las pruebas mecánicas y la muestra al azar; `--subir` sube la intensidad; `--aprender`,
  `--ajustar` y `--preferencia` guardan lo aprendido y las preferencias de la empresa.

## Skills y roles
Skill `investigar` (orquesta todo). Subagentes `bibliotecario`, `refutador` y `arbitro`; los demás roles
(encuadrador, cartógrafo, analista, editor) los aplica el asistente principal con sus fichas en
`.claude/skills/investigar/references/roles/`. También sirven `revisar-documento`, `reportes` y, en una
postulación, `red-team` (que verifica que lo afirmado tenga respaldo).

## Principios
- **Construir antes de matar es el error que todo esto existe para impedir.**
- Hecho separado de inferencia, marcado en el texto; ninguna afirmación portante sin fuente N1–N3.
- Las firmas de P0, P2 y P5 son de una persona; el asistente nunca firma por ella.
- Una conclusión tumbada se retira, no se matiza.
- Decisiones legales, de inversión o de salud: la investigación organiza la evidencia; deciden la persona y los
  profesionales competentes.

## Preguntas de la mini entrevista
1. ¿Qué decisión se tomará con el resultado y quién la toma (nombre)?
2. ¿Qué cuesta más: actuar sobre algo falso o dejar pasar algo cierto?
3. ¿Hay restricciones de fuentes (solo abiertas, presupuesto para bases de pago) y plazo?
4. ¿Hay un cartucho de dominio que calce, o es un rubro nuevo?
5. ¿Alimenta otro trabajo (postulación, estudio) o es el producto?
