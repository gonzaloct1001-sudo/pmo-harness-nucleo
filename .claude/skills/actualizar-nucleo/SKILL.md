---
name: actualizar-nucleo
description: Trae la versión nueva del núcleo del harness (skills, herramientas, arquetipos, plantillas, instaladores) a esta carpeta de empresa sin tocar sus proyectos ni sus datos — muestra antes qué cambia y qué hay de nuevo, respalda lo que reemplaza, ejecuta las pruebas y revierte si fallan. Úsala cuando el usuario diga "actualiza el harness", "hay una versión nueva", "trae las mejoras", o cuando reciba un zip o un enlace con una versión nueva del núcleo; también para mantener al día varias carpetas de empresa.
---

# Actualizar el núcleo

Cada carpeta de empresa trae su propia copia del núcleo (así cualquier IA la entiende sin instalar nada aparte). Las
mejoras se traen con `herramientas/actualizar_nucleo.py`, que solo reemplaza las rutas de `NUCLEO.txt`.

1. **Origen.** Usa el de `.harness/estado.yaml` (`nucleo.origen`). Si está en `pendiente`, pregunta al usuario de
   dónde viene la versión nueva: la URL del repositorio del núcleo o la carpeta donde descomprimió el zip. Ofrece
   guardarlo en `nucleo.origen` para la próxima vez.
2. **Antes:** si hay cambios sin guardar, ofrece `guardar-cambios` primero, para que la actualización quede en un commit propio.
3. **Vista previa:** `python herramientas/actualizar_nucleo.py [--desde <origen>]`. Resume al usuario en pocas líneas:
   versión actual → nueva, las novedades principales del CHANGELOG, cuántos archivos cambian y, si aparecen,
   - **modificados a mano** (se respaldan y se reemplazan: si eran ajustes propios, conviene moverlos a la carpeta
     del proyecto o de la empresa, regla 8 de `AGENTS.md`);
   - **propios de la empresa** dentro de carpetas del núcleo (se conservan);
   - **sin registro** (carpeta antigua sin `.harness/nucleo-instalado.csv`): no se borran; revisa si son restos de
     una versión anterior.
   Aclara que los proyectos, la empresa y los documentos no se tocan.
4. **Aplicar**, con el visto bueno: `python herramientas/actualizar_nucleo.py [--desde <origen>] --aplicar`.
   Ejecuta las pruebas (varios minutos) y, si fallan, revierte solo. Si la carpeta es un repositorio, deja el commit
   «Actualización del núcleo a <versión>».
5. **Después:** si cambiaron `AGENTS.md`, `CLAUDE.md` o una skill, las reglas nuevas rigen desde la próxima sesión:
   sugiere cerrar y abrir la sesión de la IA. Ofrece `guardar-cambios` para subir el commit.

Varias empresas: repite en cada carpeta (cada una es independiente). Si el usuario mantiene el núcleo, el origen de
todas puede ser el mismo repositorio del núcleo.
