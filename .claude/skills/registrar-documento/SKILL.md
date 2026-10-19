---
name: registrar-documento
description: Incorpora documentos contractuales y comerciales al proyecto — contrato, anexos, enmiendas, adendas, órdenes de compra, propuestas comerciales, reevaluaciones, actas de aceptación — generando su ficha resumen, archivándolos con la nomenclatura correcta y actualizando la línea base vigente. Úsala siempre que el usuario entregue o mencione uno de estos documentos, o pregunte qué dice el contrato vigente sobre plazo, monto, hitos o multas.
---

# Registrar documento contractual o comercial

## Nomenclatura
| Tipo | Id | Carpeta |
|---|---|---|
| Contrato base | C00 | `contractual/contrato/C00-<tema>/` |
| Anexo | A01, A02… | `contractual/contrato/anexos/A01-<tema>/` |
| Enmienda / adenda | E01, E02… | `contractual/contrato/enmiendas/E01-AAAA-MM-<tema>/` |
| Propuesta comercial | P01… | `contractual/comercial/propuestas/P01-<tema>/` |
| Reevaluación | R01… | `contractual/comercial/reevaluaciones/R01-<tema>/` |

Cada carpeta contiene `ficha.md` (desde `contractual/_plantillas/ficha.md`) y el original como
`original.<ext>`. Los originales **no se suben a Git** (ver `.gitignore`); si el usuario prefiere no
guardar el original localmente, anota en la ficha dónde está (repositorio documental oficial).
El texto completo queda en `fuentes/` (réplica fiel, en el repositorio privado), que genera `extraer_entrada.py`; anota
su ruta en el campo `replica:` de la ficha. **En otro computador** (sin el original), lee y cita la réplica.

## Pasos
1. Lee el documento completo. Si es PDF escaneado sin texto, avísalo y pide una versión con texto o
   extrae lo posible de las imágenes marcando la confianza.
2. Clasifícalo y propone id y carpeta. Confirma con el usuario.
3. Completa la ficha: resumen, tabla de cláusulas clave **con referencia a cláusula o página**, qué modifica
   y alertas de gestión (plazos de aviso, obligaciones, condiciones de aceptación, garantías que vencen).
4. Agrega la fila a `contractual/registro-documentos.csv`. Si reemplaza a otro, marca el anterior `vigente = no`.
5. Si modifica la línea base (alcance, plazo, monto, hitos, multas):
   - Muestra el antes y el después.
   - Tras confirmar, actualiza `contractual/linea-base-vigente.md` (valor, origen y fila en el historial)
     y `linea_base` en `proyecto.yaml`.
   - Revisa efectos en cascada: cronograma (¿hay tareas fuera del nuevo plazo?), catálogo de reportes,
     riesgos. Propón los ajustes; no los apliques sin confirmación.
   - Si viene de un cambio aprobado, vincúlalo en `registro-cambios.csv` (`documento_formal`) y pasa el
     cambio a estado "formalizada".
6. Mueve el original desde `_entrada/` a su carpeta. Sugiere `guardar-cambios`.

## Enmiendas en un programa (arquetipo programa)
Si el proyecto es un programa, una enmienda modifica el contrato padre y puede afectar a uno, varios o ningún
subproyecto. Además de la ficha y la línea base del programa, registra cada efecto por subproyecto (plazo, alcance,
monto, hito) en `contractual/afectaciones.csv` y aplícalo siguiendo `gestionar-programa` (sección "Enmiendas que
afectan subproyectos"). Termina con `python herramientas/programa.py <programa>` sin afectaciones pendientes.

## Consultas
Para preguntas como "¿cuándo termina el contrato?" responde desde `linea-base-vigente.md` citando el
documento de origen. Si la pregunta es de interpretación, cita la cláusula y recuerda que prevalece el
texto original y la opinión del área legal.
