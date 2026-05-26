@echo off
REM Script para iniciar el servidor con soporte WebSocket
REM Usa Daphne en lugar de runserver para soportar Channels/WebSockets

echo ========================================
echo   Turnero Django - Servidor WebSocket
echo ========================================
echo.
echo Iniciando servidor con Daphne...
echo El monitor se actualizará en tiempo real
echo.
echo URL: http://127.0.0.1:8000
echo Monitor: http://127.0.0.1:8000/turnos/monitor/
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Iniciar Daphne
daphne -b 127.0.0.1 -p 8000 turnero.asgi:application

pause
