---
name: definir-pauta
description: Construye la pauta de evaluación de un proceso (fondo concursable, licitación, concurso, selección de proveedores) a partir de sus bases o de una conversación — requisitos de admisibilidad excluyentes y subsanables, criterios con ponderación, descriptores por nivel de puntaje, umbrales y desempate — y detecta ambigüedades de las bases. Úsala cuando el usuario entregue bases de un concurso o licitación, quiera armar o ajustar una pauta o rúbrica de evaluación, o vaya a iniciar la evaluación de propuestas.
---

# Definir pauta de evaluación

Resultado: `evaluacion/pauta.yaml` completa y coherente, más las métricas `crit_<id>` en `metricas/metricas.yaml`.
El proyecto debe tener el arquetipo `evaluacion` (si no, créalo con `nuevo-proyecto` o `crear_proyecto.py`).

**Modo oferente (arquetipo `postulacion`): pauta inversa.** Cuando quien trabaja es el que postula, el resultado es
`postulacion/pauta-inversa.yaml` (mismo formato, con `fuente` en cada criterio) y no se agregan métricas `crit_<id>`.
Además de los pasos siguientes:
- Agrega `umbrales.puntaje_objetivo`: el puntaje que el equipo se fija para tener opción real de adjudicar
  (por defecto, mínimo de las bases + 0,5, o más si la convocatoria es muy competida; confirmarlo con el usuario).
- Completa `temas_ganadores` por criterio junto con la estrategia (`postulacion/estrategia.md`).
- Las reglas de evaluación del barrido (`barrido-requisitos.csv`, tipo `evaluacion`) se marcan `descartado` con
  motivo "incorporada en pauta-inversa.yaml".
- Las ambigüedades van como consultas en `postulacion/consultas.csv`, dentro del plazo del foro.

## Pasos
1. **Leer las bases** (en `_entrada/` o `documentos/`; conviértelas con `extraer_entrada.py` si hace falta).
   Si no hay bases, construye la pauta por conversación: objetivo del proceso y qué se valora.
2. **Extraer**, citando artículo o sección de las bases:
   - convocatoria: nombre, fecha de cierre, presupuesto total, monto máximo por propuesta, moneda;
   - admisibilidad: cada requisito, y si es **excluyente** o **subsanable** (si las bases no lo dicen, márcalo como duda);
   - criterios y subcriterios con su ponderación; escala de puntaje; umbrales mínimos; reglas de desempate.
3. **Completar los descriptores por nivel** de cada criterio (al menos para el mínimo, el medio y el máximo
   de la escala). Si las bases los traen, cópialos fielmente; si no, redáctalos como conductas observables
   en la propuesta ("presenta cronograma con hitos verificables y responsables") y márcalos como
   *propuestos*, para validación del usuario o del mandante.
4. **Validar la coherencia**: ponderaciones que suman 1, escala única, criterios sin superposición
   (un mismo aspecto no debe puntuarse dos veces), umbrales alcanzables, desempate definido.
5. **Listar ambigüedades** de las bases que convenga aclarar con el mandante antes de evaluar
   (ej.: "no se indica si la carta de apoyo es excluyente").
6. **Escribir** `pauta.yaml` y agregar a `metricas.yaml` una métrica por criterio:
   `{id: crit_<id>, nombre: <nombre>, nivel: item, unidad: "", direccion: mayor_mejor, frecuencia: a_pedido, fuente: herramientas/puntaje_pauta.py, definicion: <descripción>, umbral_rojo: <mínimo si existe>}`.
7. **Presentar** la pauta en una tabla (criterio, ponderación, qué se evalúa, descriptor del nivel máximo) con
   las ambigüedades y los descriptores propuestos, y pedir confirmación.
8. Si hay varios evaluadores, recomienda una **calibración**: que todos evalúen la misma propuesta de prueba
   y comparen puntajes antes de evaluar el resto.
