# Perfil: postulación a un instrumento CORFO

- **Arquetipos:** `postulacion` (+ `ejecucion` si se adjudica).
- **Crear:** `python herramientas/crear_proyecto.py <slug> --arquetipos postulacion --perfil biblioteca/perfiles/fondo-corfo`

> **Confirmar siempre contra las bases vigentes del instrumento y su convocatoria.** CORFO tiene muchos
> instrumentos (emprendimiento, innovación, fomento productivo, inversión) y cada uno fija sus propios porcentajes,
> topes, requisitos, plazos y criterios, que además cambian entre convocatorias. Este perfil dice *qué revisar*,
> no *cuánto vale*.

## Fuentes oficiales a consultar
- Sitio de CORFO (ficha del instrumento, bases técnicas y administrativas, preguntas frecuentes).
- Portal Único de Fondos Concursables del Estado (fondos.gob.cl): ficha y enlace a la convocatoria.
- Sistema de postulación en línea que indique la convocatoria.

## Qué suele exigir (verificar en las bases)
- Tipo de postulante admitido (persona natural o jurídica, tamaño de empresa, antigüedad, ventas) y postulación
  directa o a través de una **entidad patrocinadora, gestora u operadora** según el instrumento.
- **Cofinanciamiento:** porcentaje máximo que financia CORFO, tope en monto, aporte mínimo del postulante y qué parte
  debe ser **pecuniaria** (en efectivo) frente a **no pecuniaria** (valorizada); suele variar por tamaño de empresa.
- Ítems de gasto financiables, topes por ítem, gastos no financiables y forma de valorizar aportes no pecuniarios.
- Antecedentes legales y tributarios (inicio de actividades, carpeta tributaria, certificado de vigencia, poderes del
  representante), con antigüedad máxima de emisión.
- Formulario en línea con secciones y límites de caracteres; anexos y cartas de compromiso de asociados.
- Si se adjudica: convenio, garantías (por ejemplo, para anticipos), informes de avance y **rendición de gastos**.

## Etapas típicas a revisar en `postulacion/etapas.yaml`
Algunas convocatorias tienen revisión de **pertinencia** o admisibilidad previa, evaluación técnica y comité de
asignación; otras, pitch o entrevista. Agrégalas como etapas si las bases las definen.

## Riesgos frecuentes
Aporte pecuniario insuficiente; presupuesto con gastos no financiables; antecedentes legales vencidos; límite de
caracteres del formulario; cartas de asociados sin firma; mezclar requisitos de otra convocatoria del mismo
instrumento; sobrecompromiso de resultados que luego deben rendirse.

## Preguntas al crear el proyecto
1. ¿Qué instrumento y convocatoria exactos (año, región, enlace a las bases)?
2. ¿Postula directo o con entidad patrocinadora u operadora? ¿Cuál?
3. ¿Tamaño de la empresa (según la definición de las bases)? Afecta el cofinanciamiento.
4. ¿Cuánto puede aportar el postulante en efectivo y cuánto valorizado?
