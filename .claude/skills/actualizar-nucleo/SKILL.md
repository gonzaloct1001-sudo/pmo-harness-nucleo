---
name: actualizar-nucleo
description: Trae la versión nueva del núcleo (skills, herramientas, arquetipos, plantillas, reglas) a esta carpeta sin tocar proyectos ni datos: muestra antes qué cambia y qué hay de nuevo, respalda, prueba y revierte si falla. Úsala con «actualiza el harness», «hay una versión nueva», «trae las mejoras», o al recibir un zip o enlace del núcleo.
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/trabajo.md`, `reglas/datos.md`, `reglas/nucleo.md`, `reglas/organizacion.md`.

# Actualizar el núcleo

Cada carpeta de empresa trae su propia copia del núcleo (así cualquier IA la entiende sin instalar nada aparte). Las
mejoras se traen con `herramientas/actualizar_nucleo.py`, que solo reemplaza las rutas de `NUCLEO.txt`.

1. **Origen.** Usa el de `.harness/estado.yaml` (`nucleo.origen`). Si está en `pendiente`, pregunta al usuario de
   dónde viene la versión nueva: la URL del repositorio del núcleo o la carpeta donde descomprimió el zip. Ofrece
   guardarlo en `nucleo.origen` para la próxima vez.
2. **Antes:** si hay cambios sin guardar, ofrece `guardar-cambios` primero, para que la actualización quede en un commit propio.
3. **Vista previa:** `python herramientas/actualizar_nucleo.py [--desde <origen>]`. Resume al usuario en pocas líneas:
   versión actual → nueva, las novedades principales del CHANGELOG, cuántos archivos cambian y, primero, la sección
   **«Lo tuyo en esta actualización»**: nada propio se pierde ni se pisa en silencio. Si aparecen, explícalos así:
   - **cambian de nombre**: algo propio (una skill, un archivo) se llama igual que algo nuevo del núcleo; lo propio
     queda entero como `<nombre>-propia` (o `<nombre>-propio.<ext>`) y lo del núcleo entra con el nombre original.
     Si un hook o un permiso apuntaba al nombre anterior, ofrece corregirlo después;
   - **se conservan como los dejaste**: archivos del núcleo que se modificaron aquí y que el núcleo nuevo no cambia;
   - **se fusionan**: `.claude/settings.json`, `.gitignore` y `requirements.txt`; entra lo del núcleo nuevo y queda
     lo que el usuario agregó (permisos, hooks, patrones que nunca se suben, dependencias);
   - **modificados a mano** que el núcleo nuevo también cambia: se respaldan y se reemplazan. Dilo con sus nombres;
     después de aplicar, ofrece revisar el respaldo y llevar lo propio a `empresa/extensiones/`, a `empresa/estilo.md`
     o a una mejora (queda anotado un recordatorio en `mejoras.py`);
   - **propios de la empresa** dentro de carpetas del núcleo (se conservan);
   - **pruebas propias** (`empresa/extensiones/pruebas*.py`): se ejecutan antes y después; si una que pasaba deja de
     pasar, la actualización se revierte sola y dice cuál. Entonces ayuda a ajustar la extensión y repite;
   - **se completa `empresa/`** con lo que la plantilla nueva trae y la carpeta no tiene (archivos y bloques nuevos de
     `empresa.yaml`), sin cambiar nada existente;
   - **sin registro** (carpeta antigua sin `.harness/nucleo-instalado.csv`): no se borran; revisa si son restos de
     una versión anterior.
   Aclara que los proyectos, la empresa y los documentos no se tocan.
4. **Aplicar**, con el visto bueno: `python herramientas/actualizar_nucleo.py [--desde <origen>] --aplicar`.
   Ejecuta las pruebas (varios minutos) y, si fallan, revierte solo. Si la carpeta es un repositorio, deja el commit
   «Actualización del núcleo a <versión>». Si el núcleo nuevo trae un actualizador distinto, es ese el que corre.
   **Si la carpeta venía de 2.6.0 o anterior** (su actualizador no sabía fusionar ni completar), ejecuta el mismo
   comando una segunda vez sin preguntar: la segunda pasada completa `empresa/`; y si la vista previa de la primera
   listó `.claude/settings.json` como «modificado a mano», copia del respaldo los permisos propios que faltaran.
5. **Después:** si cambiaron `AGENTS.md`, `CLAUDE.md` o una skill, las reglas nuevas rigen desde la próxima sesión:
   sugiere cerrar y abrir la sesión de la IA. Ofrece `guardar-cambios` para subir el commit.

Varias empresas: repite en cada carpeta (cada una es independiente). Si el usuario mantiene el núcleo, el origen de
todas puede ser el mismo repositorio del núcleo.
