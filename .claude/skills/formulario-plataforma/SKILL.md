---
name: formulario-plataforma
description: Formulario de una plataforma de postulación (CORFO, fondos.gob.cl u otra) cuando no hay un documento descargable que llenar — reconstruye los campos (pregunta, obligatoriedad, límite de caracteres, ayuda, opciones) desde los formularios vacíos o impresos del portal o desde un Word con las instrucciones en color, redacta y controla las respuestas (límites, obligatorios, caracteres raros pegados desde la web), genera el Word de trabajo con la pregunta, la instrucción en azul y el conteo, y la hoja de carga para copiar y pegar campo por campo en la plataforma. Úsala cuando el usuario diga que la postulación se llena en línea, que no hay formulario, que tiene que transcribir o copiar y pegar en el portal, pregunte cuántos caracteres lleva, o pida el formulario de trabajo o la hoja para cargar.
---

# Formulario de plataforma

Herramienta: `python herramientas/formulario.py`. El formulario vive en `postulacion/formulario.yaml` (un campo por
pregunta); las respuestas cortas van en el campo `respuesta` y las largas en `propuesta/campos/<id>.md`.

## 1. Reconstruir el formulario (una vez por convocatoria)
1. Consigue la estructura de la plataforma, en este orden de preferencia:
   - los **formularios vacíos o impresos del portal** (PDF «Formato vacío», impresión de cada pantalla);
   - un **Word** donde el usuario copió las preguntas con las instrucciones en color (como el azul de su Word de CORFO);
   - **capturas de pantalla**: léelas tú y escribe los campos directamente en el YAML.

   Si hay versiones vacías y llenas del mismo formulario, usa solo las vacías: las llenas duplican campos y sus
   respuestas se confunden con títulos. Las respuestas de una versión llena se traen después, campo por campo.
2. `python herramientas/formulario.py proyectos/<slug> --reconstruir <archivos>` (con `--color 0000FF` si el Word usa
   otro color además del azul) → `postulacion/formulario.borrador.yaml`.
3. **Revísalo con el usuario contra la plataforma**: que estén todas las preguntas, cuáles son obligatorias, los límites
   de caracteres (incluidos los espacios), las opciones de las selecciones y el orden. Completa `plataforma:` y guárdalo
   como `postulacion/formulario.yaml`. El borrador es una ayuda: lo que manda es la plataforma.
4. Los campos obligatorios son requisitos: súmalos a la matriz (`matriz-cumplimiento`) si no están.

## 2. Redactar y controlar
1. Respuestas largas en `propuesta/campos/<id>.md` (encabezado con `campo:` y `responde_a:` para ligarlas a requisitos
   y criterios de la pauta inversa); cortas en `respuesta:`. Estilo de `contexto/estilo.md`, sin rastros del proceso.
2. `python herramientas/formulario.py proyectos/<slug>` en cada ronda: campos que exceden su límite, obligatorios vacíos y
   caracteres raros. Para acortar, reescribe con sentido: nunca cortes una frase a la mitad. Algunas plataformas
   cuentan cada salto de línea como dos caracteres: el control avisa cuando eso haría exceder el límite.
3. Caracteres raros (invisibles o de otro alfabeto, típicos de copiar desde la web): `--limpiar` corrige los inequívocos;
   los dudosos (como una «з» cirílica, que parece un 3) corrígelos a mano.
4. El estado de la postulación (`postulacion.py`) y la compuerta de entrega exigen cero campos excedidos y cero
   obligatorios vacíos.

## 3. Salidas
- **Word de trabajo** para revisar con el equipo, con el formato del usuario (pregunta, instrucción en azul, conteo,
  respuesta): `--word` → `propuesta/salida/formulario-trabajo_<fecha>.docx`. Pasa `verificar_autoria.py`.
- **Hoja de carga** para el día de la carga: `--hoja-carga --abrir` → una página con cada campo y un botón «Copiar»;
  el usuario pega campo por campo en la plataforma.
- **Después de cargar**: pide al usuario descargar o imprimir a PDF el formulario enviado desde la plataforma y el
  comprobante, y dejarlos en `entrega/final/`. Esa es la versión final oficial (así nunca queda la duda de cuál fue).

## Qué no hacer
- No ingresar a la plataforma ni pedir la Clave Única u otras credenciales: la carga la hace el responsable designado.
- No dar por buena una respuesta que exceda el límite «porque la plataforma la cortará»: se corta donde no conviene.
