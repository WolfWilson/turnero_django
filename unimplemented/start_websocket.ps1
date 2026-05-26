# Script para iniciar el servidor con soporte WebSocket
# Usa Daphne en lugar de manage.py runserver

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Turnero Django - Servidor WebSocket" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Iniciando servidor con Daphne..." -ForegroundColor Yellow
Write-Host "El monitor se actualizará en tiempo real" -ForegroundColor Green
Write-Host ""
Write-Host "URL: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "Monitor: http://127.0.0.1:8000/turnos/monitor/" -ForegroundColor White
Write-Host ""

# Activar entorno virtual si existe
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
}

# Iniciar Daphne
daphne -b 127.0.0.1 -p 8000 turnero.asgi:application
