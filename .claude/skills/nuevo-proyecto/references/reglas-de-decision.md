# Reglas de decisión del alta

## 1. Jerarquía de fuentes (de mayor a menor peso)
1. Documento firmado o formal vigente (contrato, enmienda, orden de compra, acta de comité aprobada).
2. Documento formal posterior que modifica a otro (una enmienda prevalece sobre el contrato en lo que modifica).
3. Planificación oficial vigente (última versión del cronograma o Gantt).
4. Reportes formales emitidos (el más reciente prevalece).
5. Actas y minutas.
6. Correos (el más reciente prevalece, salvo que contradiga un documento formal).
7. Propuestas y cotizaciones (solo para lo que el contrato no cubre).
8. Conversaciones con otras IA y notas informales.

## 2. Reglas de desempate
- **Recencia:** entre fuentes del mismo nivel, gana la más reciente (fecha del documento, no del archivo).
- **Especificidad:** un dato preciso ("30-04-2027") gana sobre uno vago ("fines de abril") del mismo nivel.
- **Coherencia:** si un valor encaja con el resto de datos y otro no, gana el coherente (confianza media).
- **Nombres de personas y cargos:** usar la forma más completa y formal encontrada; si hay cargos
  distintos, el del documento más reciente.
- **Avance:** el último reporte formal o planilla de control; si el cronograma tiene avance más reciente, el cronograma.

## 3. Nivel de confianza
- **Alta:** fuente de nivel 1–3 sin contradicción, o contradicción resuelta por la jerarquía.
- **Media:** fuente de nivel 4–6, o dato inferido de forma razonable (ej.: poder alto para quien preside el comité),
  o contradicción resuelta solo por recencia o coherencia.
- **Baja:** solo fuentes de nivel 7–8, inferencia débil, o contradicción entre fuentes del mismo nivel y fecha.

## 4. Cuándo preguntar
| | Confianza alta | Media | Baja |
|---|---|---|---|
| Dato crítico (C) | decidir | decidir y marcar revisar | **preguntar** |
| Importante (I) | decidir | decidir y marcar revisar | decidir por defecto y marcar revisar, o preguntar si no hay defecto |
| Opcional (O) | decidir | decidir | defecto |

Pregunta también, sin importar la tabla, cuando:
- dos documentos formales vigentes se contradicen (ej.: dos enmiendas con fechas incompatibles);
- hay que elegir entre alternativas con consecuencias contractuales o de comunicación (ej.: qué logo usar
  en reportes al cliente, a quién se envía el reporte);
- el material sugiere que hay documentos clave que no se cargaron (ej.: se menciona la "Enmienda N°2" pero no está).

## 5. Valores inferidos permitidos (siempre con confianza media y registrados)
- Poder/interés de stakeholders según su rol (preside comité → poder alto; usuario clave → interés alto).
- Estrategia de gestión de stakeholders según poder/interés.
- Evaluación de probabilidad e impacto de riesgos mencionados sin evaluar.
- Subproyectos a partir del primer nivel del cronograma o de las secciones de los reportes.
- Cadencia de un reporte a partir de las fechas de la serie encontrada.

## 6. Nunca inferir
- Montos, fechas contractuales, multas o garantías sin fuente.
- Aprobaciones de cambios no documentadas.
- Responsables de acuerdos que el documento no nombra.
