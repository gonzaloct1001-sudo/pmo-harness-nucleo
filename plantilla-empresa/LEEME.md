# Empresa

Lo común a todos los proyectos de la empresa dueña de esta carpeta. Cada proyecto hereda de aquí lo que no define.

| Qué | Dónde | Para qué |
|---|---|---|
| Identidad, responsable, marca, autoría y réplicas | `empresa.yaml` | Los documentos de todos los proyectos salen con esta marca y a este nombre |
| Banco de antecedentes | `contenidos/` | Descripción de la empresa, experiencia, CVs, certificados y estados financieros, con su vigencia en `registro.csv`. Los archivos van en `contenidos/archivos/` y **no se suben a Git** |
| Estilo de redacción | `estilo.md` | Tono, vocabulario y puntuación de la empresa; los proyectos nuevos parten de aquí |
| Logo | `marca/logo.png` | Lo usan todos los proyectos que no tengan uno propio |
| Plantillas Word, Excel o PowerPoint | `plantillas/` | Formatos comunes (por ejemplo, el informe de avance o la carta de presentación) |
| Formatos de reportes | `reportes/catalogo/` | Definiciones de reportes que se copian a cada proyecto nuevo |

Reglas:
- Una carpeta es una empresa. Para otra empresa: `python herramientas/nueva_empresa.py "<Nombre>" --destino <carpeta>`.
- Los certificados vencen: registra `vigente_hasta` en `contenidos/registro.csv`. Antes de cada cierre, el estado de
  la postulación avisa qué documento estaría vencido.
- Los textos reutilizables (descripción, experiencia) se adaptan a cada convocatoria: nunca se copian sin ajustarlos
  a los criterios de evaluación.
