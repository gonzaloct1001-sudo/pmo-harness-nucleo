@echo off
rem Instalador del PMO Harness para Windows: doble clic para dejar listo el computador.
rem Instala solo para tu usuario (no pide permiso de administrador) y no hace preguntas tecnicas.
rem No instala VS Code ni el asistente de IA. Detalle en herramientas\preparar_pc.ps1
rem La ruta del script va relativa: algunos controles de seguridad detienen PowerShell si su linea de comando trae la
rem ruta completa de una carpeta vigilada (por ejemplo, la que tiene abierta un editor con IA).
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "herramientas\preparar_pc.ps1" -DobleClic %*
rem Si PowerShell no pudo ni empezar, deja leer el error (sin esperar para siempre)
if errorlevel 1 timeout /t 120
