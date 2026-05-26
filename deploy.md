# Deploy — Turnero (IIS + uvicorn + httpPlatformHandler) — web03

## Referencia rápida

| Elemento       | Valor                              |
|----------------|------------------------------------|
| App Pool       | `AppPool_Turnero`                  |
| Sitio IIS      | `Turnero`                          |
| Carpeta física | `C:\inetpub\Sites\Turnero`         |
| Módulo IIS     | `httpPlatformHandler`              |
| Arranque       | `start_uvicorn.bat %HTTP_PLATFORM_PORT%` |
| Log            | `logs\wrapper_stdout.log`          |
| Settings       | `turnero.settings`                 |
| ASGI app       | `turnero.asgi:application`         |

---

## Despliegue inicial

```cmd
xcopy /E /I /Y ".\*" "C:\inetpub\Sites\Turnero\"
cd C:\inetpub\Sites\Turnero
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
mkdir logs
venv\Scripts\python.exe manage.py collectstatic --noinput
venv\Scripts\python.exe manage.py migrate
```

### `.env` de producción

```env
SECRET_KEY=<generar con get_random_secret_key()>
DEBUG=False
ALLOWED_HOSTS=web03,<IP>

DB_NAME=Turnero
DB_HOST=web03
SQL_USER=turnero_user
SQL_PASS=<password>
DB_DRIVER=SQL Server Native Client 11.0

APORTES_DB_HOST=sql01
```

---

## App Pool y Sitio (PowerShell Admin)

```powershell
Import-Module WebAdministration

New-WebAppPool -Name "AppPool_Turnero"
Set-ItemProperty IIS:\AppPools\AppPool_Turnero managedRuntimeVersion ""
Set-ItemProperty IIS:\AppPools\AppPool_Turnero startMode AlwaysRunning
Set-WebConfigurationProperty `
    -Filter '/system.applicationHost/applicationPools/add[@name="AppPool_Turnero"]' `
    -Name "processModel.idleTimeout" -Value "00:00:00"

New-Website -Name "Turnero" `
            -PhysicalPath "C:\inetpub\Sites\Turnero" `
            -ApplicationPool "AppPool_Turnero" `
            -Port 80 -Force

icacls "C:\inetpub\Sites\Turnero" /grant "IIS AppPool\AppPool_Turnero:(OI)(CI)M" /T
```

---

## Operaciones frecuentes

```powershell
# Reciclar (recarga uvicorn, equivale a reiniciar la app)
Restart-WebAppPool -Name "AppPool_Turnero"

# Log en vivo
Get-Content "C:\inetpub\Sites\Turnero\logs\wrapper_stdout.log" -Wait -Tail 50

# Verificar httpPlatformHandler instalado
Get-WebConfigurationProperty -pspath 'MACHINE/WEBROOT/APPHOST' `
    -filter "system.webServer/globalModules/add[@name='httpPlatformHandler']" -name "."

# Probar arranque manual (fuera de IIS)
cd C:\inetpub\Sites\Turnero
call start_uvicorn.bat 8765
```

---

## Troubleshooting

| Síntoma | Causa | Acción |
|---|---|---|
| `500.19` al cargar | `web.config` mal formado o sin permisos de lectura | Revisar XML; verificar `icacls` |
| `502.5` proceso no arranca | Ruta del venv incorrecta o módulos no instalados | Ejecutar `call start_uvicorn.bat 8765` manualmente y ver salida |
| IIS descarga el `.bat` | `httpPlatformHandler` no registrado | Instalar módulo; agregar `<clear />` en `<handlers>` |
| `404` en todas las rutas | Handler de `StaticFile` toma precedencia | Agregar `<clear />` antes del `<add name="Turnero" .../>` |
| Sin estáticos | `collectstatic` no ejecutado o permisos en `staticfiles/` | Re-ejecutar `collectstatic`; verificar `icacls` |
| Error de DB al iniciar | Driver ODBC no instalado o credenciales incorrectas | Verificar `SQL Server Native Client 11.0` en el servidor; revisar `.env` |

### `<clear />` en handlers (usar solo si hay conflicto confirmado)

```xml
<handlers>
    <clear />
    <add name="Turnero" path="*" verb="*"
         modules="httpPlatformHandler" resourceType="Unspecified" />
</handlers>
```

> Las reglas `<rewrite>` en `web.config` ya protegen `static/` y `media/`. `<clear />` elimina todos los handlers heredados del servidor, lo cual puede romper otros sitios si el config se hereda.

---

## Actualizar código en producción

```cmd
cd C:\inetpub\Sites\Turnero

REM 1. Copiar nuevos archivos
xcopy /E /I /Y "C:\ruta\fuente\*" "."

REM 2. Instalar nuevas dependencias (si hubiera)
venv\Scripts\python.exe -m pip install -r requirements.txt

REM 3. Migraciones (solo tablas managed=True: MotivoCierre, LlamadaTurno)
venv\Scripts\python.exe manage.py migrate

REM 4. Recolectar estáticos
venv\Scripts\python.exe manage.py collectstatic --noinput

REM 5. Reciclar App Pool
powershell -Command "Restart-WebAppPool -Name 'AppPool_Turnero'"
```


