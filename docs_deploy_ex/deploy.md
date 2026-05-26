# Deploy — Gestión de Gestores (IIS + uvicorn + httpPlatformHandler)

## Nombres de referencia

| Elemento         | Valor                                      |
|------------------|--------------------------------------------|
| App Pool         | `AppPool_GestionGestores`                  |
| Sitio IIS        | `Gestion_Gestores`                         |
| Carpeta física   | `C:\inetpub\Sites\Gestion_Gestores`        |
| Log de arranque  | `...\logs\wrapper_stdout.log`              |

---

## Pasos rápidos

### 1 — Copiar archivos y crear venv

```cmd
xcopy /E /I /Y ".\*" "C:\inetpub\Sites\Gestion_Gestores\"
cd C:\inetpub\Sites\Gestion_Gestores
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
mkdir logs
```

### 2 — Configurar `.env` de producción

```env
SECRET_KEY=<nueva-clave>
DEBUG=False
ALLOWED_HOSTS=web03,<IP>

DB_HOST_CONS=SQL01
DB_NAMEC_CONS=Aportes
DB_DRIVER_CONS=SQL Server Native Client 11.0
SQL_USER_CONS=user_4gestores
SQL_PASS_CONS=<password>
```

Generar SECRET_KEY:
```cmd
venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3 — Collectstatic y check

```cmd
venv\Scripts\python.exe manage.py collectstatic --noinput --settings=config.settings.production
venv\Scripts\python.exe manage.py check --settings=config.settings.production
```

---

## App Pool y Sitio (PowerShell como Admin)

```powershell
Import-Module WebAdministration

# App Pool — sin runtime .NET, sin idle timeout
New-WebAppPool -Name "AppPool_GestionGestores"
Set-ItemProperty IIS:\AppPools\AppPool_GestionGestores managedRuntimeVersion ""
Set-ItemProperty IIS:\AppPools\AppPool_GestionGestores startMode AlwaysRunning
Set-WebConfigurationProperty `
    -Filter '/system.applicationHost/applicationPools/add[@name="AppPool_GestionGestores"]' `
    -Name "processModel.idleTimeout" -Value "00:00:00"

# Sitio — ajustar puerto si 80 está ocupado
New-Website -Name "Gestion_Gestores" `
            -PhysicalPath "C:\inetpub\Sites\Gestion_Gestores" `
            -ApplicationPool "AppPool_GestionGestores" `
            -Port 80 -Force

# Permisos de escritura para media/ y logs/
icacls "C:\inetpub\Sites\Gestion_Gestores" /grant "IIS AppPool\AppPool_GestionGestores:(OI)(CI)M" /T
```

---

## httpPlatformHandler — puntos críticos

El sitio usa **httpPlatformHandler** (no FastCGI). El módulo debe estar instalado a nivel servidor.

**Verificar que esté registrado:**
```powershell
Get-WebConfigurationProperty -pspath 'MACHINE/WEBROOT/APPHOST' `
    -filter "system.webServer/globalModules/add[@name='httpPlatformHandler']" -name "."
# Sin resultado → instalar desde Web Platform Installer o descargar el MSI de Microsoft.
```

**Conflicto de handlers — el problema más frecuente:**  
Si IIS devuelve 404 o ejecuta el `.bat` como descarga, el handler de `StaticFile` o `iisnode` está tomando el request antes que `httpPlatformHandler`.  
En `web.config` el handler ya usa `path="*" verb="*"` — si aun así falla, agregar `<clear />` antes del `<add>`:

```xml
<handlers>
    <clear />
    <add name="GestionGestores" path="*" verb="*"
         modules="httpPlatformHandler" resourceType="Unspecified" />
</handlers>
```

> ⚠ `<clear />` elimina todos los handlers heredados del servidor. Usarlo solo si hay conflicto confirmado; las reglas de static/media en `<rewrite>` ya protegen esos paths.

**El bat recibe el puerto como primer argumento** — httpPlatformHandler inyecta `%HTTP_PLATFORM_PORT%` en `web.config`:
```xml
arguments="/c &quot;%~dp0start_uvicorn.bat&quot; %HTTP_PLATFORM_PORT%"
```
No hardcodear el puerto en el bat.

---

## Prueba de arranque manual

```cmd
cd C:\inetpub\Sites\Gestion_Gestores
call start_uvicorn.bat 8765
REM → http://127.0.0.1:8765  (Ctrl+C para detener)
```

Si arranca manual pero no desde IIS → problema de permisos del AppPool o handler no registrado.

---

## Diagnóstico rápido

```powershell
# Últimas 50 líneas del log de uvicorn
Get-Content "C:\inetpub\Sites\Gestion_Gestores\logs\wrapper_stdout.log" -Tail 50

# Reiniciar IIS
iisreset /restart
```

| Síntoma                        | Causa probable                                      |
|--------------------------------|-----------------------------------------------------|
| 500.19 al cargar el sitio      | `web.config` mal formado o permisos de lectura      |
| 502.5 / proceso no arranca     | Ruta del venv incorrecta en `start_uvicorn.bat`     |
| Página en blanco / sin static  | `collectstatic` no ejecutado o permisos en `staticfiles/` |
| Login LDAP falla               | `DJANGO_CTL_LDAP_*` no configurados en `.env`       |
| Error de DB al iniciar         | Credenciales `SQL_USER_CONS`/`SQL_PASS_CONS` o driver no instalado |


