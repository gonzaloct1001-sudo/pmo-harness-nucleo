# Carpeta de entrada — aquí va TODO el material del proyecto

Esta carpeta es local: **los archivos que dejes aquí no se suben a GitHub.**
Del texto de las bases y los documentos de definición (bases, anexos, aclaraciones, lineamientos, contratos, actas e
informes) se guarda una **copia fiel en Markdown** en `fuentes/`, que sí se sube a tu repositorio **privado**: así puedes
trabajar desde otro computador o con otra IA sin los originales. De CVs, estados financieros y datos personales solo
queda una ficha; su texto no sale de este computador.

## Cómo cargar
- Deja todo lo que tengas. **No hace falta ordenar ni renombrar**: el asistente clasifica cada archivo.
- Las subcarpetas son solo una ayuda. Si no sabes dónde va algo, déjalo en `09-otros` o aquí mismo.
- Mientras más material, mejor: el asistente decide con los documentos y pregunta menos.
- Formatos: PDF, Word, Excel, PowerPoint, correos (.eml), texto, Markdown, CSV, JSON, imágenes.
  Los correos de Outlook (.msg) conviene guardarlos como .eml o PDF.

## Qué dejar, en orden de importancia

| Prioridad | Material | Subcarpeta sugerida |
|---|---|---|
| 1 | **Si vas a postular** (fondo, licitación, RFP): bases, anexos, formularios, aclaraciones y respuestas del foro. Las aclaraciones que lleguen después también van aquí: forman parte de las bases | `00-bases-y-aclaraciones` (créala si no existe) |
| 1 | Contrato, anexos, enmiendas, órdenes de compra (lo ya firmado) | `01-contratos-y-anexos` |
| 2 | Carta Gantt o cronograma vigente. **MS Project: guárdalo como XML** (Archivo > Guardar como > XML); también sirven Excel o PDF | `03-cronogramas` |
| 3 | Últimos reportes emitidos (semanales, mensuales, planillas de control, presentaciones a comité) | `04-reportes-y-plantillas` |
| 4 | Plantillas oficiales de reportes (Word, Excel, PowerPoint) | `04-reportes-y-plantillas` |
| 5 | Actas y minutas de reuniones, especialmente de comité | `05-actas-y-minutas` |
| 6 | Propuestas técnicas y comerciales, cotizaciones, reevaluaciones | `02-propuestas-y-cotizaciones` |
| 7 | Correos relevantes (acuerdos, cambios, problemas, aprobaciones) | `06-correos` |
| 8 | Conversaciones con otras IA sobre el proyecto | `07-chats-de-ia` |
| 9 | Logos, manual de marca, colores | `08-marca` |
| 10 | Organigrama, listados de contactos, registros de riesgos, cualquier otra cosa | `09-otros` |

## Conversaciones de otras IA (las rutas del menú pueden variar según la versión)
- **ChatGPT:** Configuración → Controles de datos → Exportar datos. Llega un .zip por correo: deja el archivo `conversations.json`.
- **Claude:** Configuración → Privacidad → Exportar datos. Deja el `conversations.json`.
- **Otras:** copia y pega cada conversación en un archivo `.md` o `.txt`.
Si la exportación trae conversaciones de otros temas, no importa: el asistente usa solo las relacionadas con el proyecto.

## ¿Tu proyecto ya está en marcha pero tienes pocos documentos?
No importa: deja lo que tengas y, al escribir **listo**, el asistente te hará unas pocas preguntas sobre el estado actual
(hitos, avance, problemas, riesgos, compromisos) para completar lo que los documentos no digan.

## Cuando termines
Escribe en el chat del asistente (Claude Code, Codex, Gemini u otro): **listo** (o "procesa la entrada").
