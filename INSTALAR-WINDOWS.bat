@echo off
rem Instalador del PMO Harness para Windows: revisa e instala (con tu permiso) lo necesario.
rem No instala VS Code ni el asistente de IA. Detalle en herramientas\preparar_pc.ps1
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0herramientas\preparar_pc.ps1" %*
echo.
pause
