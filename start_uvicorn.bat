@echo OFF
echo [START] Script iniciado
SET APP_PORT=%1
echo [PORT] %APP_PORT%
SET VENV_PYTHON=C:\inetpub\Sites\Gestion_Gestores\venv\Scripts\python.exe
SET PYTHONPATH=C:\inetpub\Sites\Gestion_Gestores
SET DJANGO_SETTINGS_MODULE=config.settings.production

REM Cargar variables del .env en el entorno del proceso
for /f "usebackq eol=# tokens=1,* delims==" %%A in ("C:\inetpub\Sites\Gestion_Gestores\.env") do (
    if not "%%A"=="" SET "%%A=%%B"
)

echo [PYTHONPATH] Configurado
echo [UVICORN] Iniciando...
"%VENV_PYTHON%" -m uvicorn config.asgi:application --host 127.0.0.1 --port %APP_PORT% 2>&1
echo [END] Finalizado
