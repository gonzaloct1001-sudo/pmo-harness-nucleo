# Perfil: oferta a una licitación pública en Mercado Público (Chile)

- **Arquetipos:** `postulacion` (+ `ejecucion` si se adjudica; `obra` si es construcción).
- **Crear:** `python herramientas/crear_proyecto.py <slug> --arquetipos postulacion --perfil biblioteca/perfiles/licitacion-mercado-publico`

> **Confirmar siempre contra las bases de la licitación y la normativa vigente.** Las compras públicas se rigen por
> la Ley 19.886, modificada por la Ley 21.634 (publicada en diciembre de 2023, con entrada en vigor escalonada), y
> por su reglamento vigente: confirma en chilecompra.cl qué disposiciones aplican a la fecha de la licitación.
> Montos de garantías, plazos y requisitos los fijan las bases de cada licitación.

## Fuentes oficiales a consultar
- mercadopublico.cl (ficha de la licitación, bases, anexos, foro de preguntas y respuestas, aclaraciones).
- chilecompra.cl (normativa, guías para proveedores, Registro de Proveedores, capacitación).

## Qué suele exigir (verificar en las bases)
- Estar inscrito y hábil en el **Registro de Proveedores** del Estado (según lo exijan las bases para ofertar o
  para contratar) y la declaración jurada correspondiente (incluida la información de beneficiarios finales).
- **Anexos administrativos** (identificación del oferente, declaraciones juradas de inhabilidades y conflictos de
  interés), **técnicos** (oferta técnica, experiencia, equipo, certificaciones) y **económicos** (oferta económica en
  el formato exacto de las bases).
- **Garantía de seriedad de la oferta** y **de fiel cumplimiento** cuando las bases la exijan (suele depender del
  monto), con el instrumento, monto, glosa, beneficiario, vigencia y forma de entrega que indiquen.
- Plazos del foro de preguntas, visita a terreno (si es obligatoria), cierre y apertura electrónica.
- Criterios de evaluación y ponderaciones publicados en las bases (precio, técnicos, plazo, experiencia, criterios
  de sustentabilidad o de inclusión, cumplimiento de requisitos formales) y reglas de desempate.

## Errores que suelen dejar ofertas fuera (revisar en guante blanco)
Anexo sin firma o en formato distinto al exigido; oferta económica fuera del formulario o con cifras distintas entre
anexos; garantía con glosa, monto o vigencia incorrectos o entregada fuera de plazo; documentos no cargados en la
plataforma antes del cierre; visita a terreno obligatoria no realizada; proveedor no hábil en el registro.

## Etapas típicas a revisar en `postulacion/etapas.yaml`
Agrega "visita a terreno" si es obligatoria y separa "apertura técnica" y "apertura económica" si las bases las distinguen.

## Preguntas al crear el proyecto
1. ¿ID de la licitación en Mercado Público y organismo comprador?
2. ¿El oferente está inscrito y hábil en el Registro de Proveedores?
3. ¿Exige garantía de seriedad? ¿Quién la tramita y en qué banco o aseguradora?
4. ¿Hay visita a terreno obligatoria?
