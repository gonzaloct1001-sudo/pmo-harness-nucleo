---
name: evaluacion-economica
description: Evaluación económica de una inversión o proyecto — construye el flujo de caja en un Excel con fórmulas (VAN, TIR, período de recuperación, VAN/inversión), análisis de sensibilidad y escenarios, a partir de supuestos explícitos con fuente; privada o social. Úsala cuando el usuario pida evaluar si un proyecto o inversión es rentable, calcular VAN o TIR, armar un flujo de caja, comparar alternativas de inversión, hacer una sensibilidad, o preparar la evaluación económica de un perfil, prefactibilidad o factibilidad.
---

# Evaluación económica

Herramienta: `python herramientas/modelo_economico.py <estudio/modelo/supuestos-modelo.yaml> [--salida archivo.xlsx]`
genera el Excel (hojas Supuestos, Flujo, Indicadores y Sensibilidad, todo con fórmulas) e imprime los
indicadores calculados en Python como control. Usa el arquetipo `estudio` (o agrégalo con `crear_proyecto.py`).

## Modo postulación (arquetipo `postulacion`)
Cuando el trabajo es el presupuesto de una postulación a un fondo o licitación:
1. Lee en las bases vigentes (y sus aclaraciones) las reglas de financiamiento: tope de la entidad (% y monto),
   aporte propio mínimo, parte pecuniaria mínima, topes por ítem, gastos no financiables, forma de valorizar los
   aportes no pecuniarios. **Nunca** las tomes de otra convocatoria ni de un perfil: cita la fuente de cada una.
2. Completa `economico/presupuesto.yaml` (parámetros, ítems con tope, partidas con su reparto por fuente y, si las
   bases lo piden, `meses` para el cronograma financiero).
3. `python herramientas/presupuesto_postulacion.py proyectos/<slug>/economico/presupuesto.yaml` → Excel con hojas
   Parametros, Presupuesto, Resumen, Controles (y Cronograma), todo con fórmulas modificables, y `controles.csv`.
4. Si hay controles NO CUMPLE, propone ajustes concretos (bajar la solicitud, aumentar el aporte pecuniario,
   reclasificar partidas) y muestra el efecto; la decisión de montos y aportes es del postulante.
5. Si las bases piden evaluación económica del proyecto (VAN, TIR, flujo de caja), agrégala con `modelo_economico.py`
   y verifica que el presupuesto del proyecto y el flujo usen las mismas cifras.
6. Ambos Excel salen con autoría limpia (autor del proyecto); confírmalo con `verificar_autoria.py`.

## 1. Definir el marco (preguntas mínimas, con propuesta)
- Tipo: **privada** (flujos del inversionista, con impuestos) o **social** (beneficios y costos para la
  sociedad, con precios sociales y la tasa social de la metodología oficial aplicable; confirmarla con el usuario).
- Tasa de descuento y su fundamento; horizonte y criterio de valor residual; moneda (nominal o real, sin mezclar).
- Situación base y situación con proyecto: se evalúan los flujos **incrementales**.
- Alternativas a comparar, si las hay (una carpeta o archivo de supuestos por alternativa).

## 2. Supuestos
1. Completa `estudio/modelo/supuestos-modelo.yaml`.
2. Registra cada supuesto relevante en `estudio/supuestos.csv` con **fuente**, **confianza** (alta/media/baja)
   y **sensibilidad** esperada. Sin fuente → confianza baja y se destaca en el informe.
3. No inventes cifras: si falta un dato, pídelo o usa un rango y trátalo en la sensibilidad.

## 3. Generar y verificar
1. Ejecuta el script. Si hay LibreOffice, recalcula el Excel y compara el VAN del Excel con el del control
   en Python (deben coincidir); si no coinciden, revisa antes de informar.
2. Revisa la razonabilidad: márgenes, año de recuperación, peso del valor residual en el VAN (si es muy
   alto, adviértelo), signo de los flujos.

## 4. Sensibilidad y escenarios
- Identifica las 2 o 3 variables que más mueven el VAN y el valor que lo hace cero (punto de equilibrio),
  aproximándolo con la tabla de sensibilidad o ejecutando el script con variaciones adicionales.
- Si hay escenarios (optimista, base, pesimista) en `estudio/escenarios.csv`, genera un modelo por escenario.

## 5. Informar
- Indicadores clave, supuestos críticos (baja confianza y alta sensibilidad), riesgos y la conclusión
  expresada con sus condiciones ("el proyecto es rentable si el ahorro energético supera X").
- Registra VAN, TIR y recuperación en `metricas/mediciones.csv` (métricas de nivel proyecto) para que
  aparezcan en reportes, y actualiza `estudio/hallazgos.md` y `estudio/conclusiones.md`.
- La recomendación final la toma quien decide; el modelo muestra bajo qué condiciones conviene.
