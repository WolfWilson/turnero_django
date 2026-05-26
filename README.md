# Sistema de Gestión de Turnos — Turnero Django

Sistema web interno para la emisión, llamado y atención de turnos. Desarrollado en **Django 5.x** con **Django REST Framework**. Desplegado en la intranet corporativa sobre **IIS + uvicorn** en el servidor **web03**.

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura y Stack](#arquitectura-y-stack)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Modelos de Datos](#modelos-de-datos)
5. [Ciclo de Vida de un Turno](#ciclo-de-vida-de-un-turno)
6. [Roles y Pantallas](#roles-y-pantallas)
7. [Mapa de URLs](#mapa-de-urls)
8. [API REST](#api-rest)
9. [Integración QR](#integración-qr)
10. [Prioridades Automáticas](#prioridades-automáticas)
11. [Configuración por Área](#configuración-por-área)
12. [Variables de Entorno](#variables-de-entorno)
13. [Entorno de Desarrollo Local](#entorno-de-desarrollo-local)
14. [Despliegue en Producción (IIS)](#despliegue-en-producción-iis)
15. [Base de Datos](#base-de-datos)
16. [WebSockets (Tiempo Real)](#websockets-tiempo-real)

---

## Descripción General

El sistema permite que el público solicite un turno de atención desde un **tótem táctil** (o cualquier navegador), identificándose con su DNI. Los operadores llaman turnos desde su **panel de mesa** y los directores/supervisores monitorean el estado general desde el **dashboard administrativo**. Una pantalla de **monitor público** en la sala de espera muestra en tiempo real los turnos llamados.

Los tótems pueden segmentarse por área mediante **códigos QR** impresos en la institución; al escanear el QR el ciudadano llega directamente al formulario de esa área.

---

## Arquitectura y Stack

| Capa | Tecnología |
|---|---|
| Framework web | Django 5.x |
| API REST | Django REST Framework |
| Base de datos principal | SQL Server 2014 (engine `mssql`) en `web03` |
| Base de datos secundaria | SQL Server `Aportes` en `sql01` (solo lectura, búsqueda de personas) |
| ORM | Todas las tablas de producción usan `managed=False` (esquema pre-existente) |
| Servidor de aplicación | uvicorn (WSGI/ASGI) |
| Servidor web | IIS 10 + httpPlatformHandler |
| Frontend | Bootstrap 5.3, Material Icons Outlined, Montserrat/Roboto |
| Tiempo real (opcional) | Django Channels + WebSocket |
| Autenticación | Django Auth + tablas `Usuario` / `UsuarioRol` propias |

---

## Estructura del Proyecto

```
turnero_django/
├── turnero/              # Configuración Django (settings, urls, asgi, wsgi, routing)
├── api/                  # API REST con DRF (serializers, views, urls)
├── apps/
│   ├── core/             # Modelos, servicios de negocio, consumers WebSocket
│   ├── turnos/           # Tótem público y monitor de sala de espera
│   ├── atencion/         # Panel del operador
│   └── administracion/   # Dashboard del director
├── templates/            # Plantillas HTML por rol/app
│   ├── registration/     # Login
│   ├── turnos/           # Tótem, monitor, confirmación
│   ├── operador/         # Panel de mesa
│   └── admin/            # Dashboard administrativo
├── static/
│   ├── css/              # Estilos por pantalla
│   └── js/               # Scripts: SPA del tótem, WebSocket, dashboard
├── docs/                 # Documentación técnica extendida
├── scripts/              # SQL de creación/migración del esquema
├── web.config            # Configuración IIS + httpPlatformHandler
├── start_uvicorn.bat     # Script de arranque para IIS
└── .env                  # Variables de entorno (NO versionar)
```

---

## Modelos de Datos

Todos los modelos en `apps/core/models.py` están mapeados a tablas SQL Server existentes (`managed=False`). Las únicas excepciones son `MotivoCierre` y `LlamadaTurno` (`managed=True`).

### Entidades principales

| Modelo | Tabla SQL | Descripción |
|---|---|---|
| `Usuario` | `Usuario` | Usuarios del sistema (no usa `django.contrib.auth.User` directamente) |
| `Rol` | `Rol` | Roles: Administrador, Director, Operador, Supervisor |
| `UsuarioRol` | `UsuarioRol` | Asignación usuario ↔ rol |
| `Area` | `Area` | Sector u oficina de atención |
| `AreaAdministrador` | `AreaAdministrador` | Administradores por área |
| `AreaUsuario` | `AreaUsuario` | Operadores asignados a un área |
| `Persona` | `Persona` | Ciudadano identificado por DNI |
| `Mesa` | `Mesa` | Puesto físico de atención dentro de un área |
| `Tramite` | `Tramite` | Tipo de trámite habilitado en un área |
| `MesaTramite` | `MesaTramite` | Qué trámites puede atender cada mesa (M2M) |
| `TramiteOperador` | `TramiteOperador` | Trámites habilitados por operador |
| `EstadoTicket` | `EstadoTicket` | Catálogo de estados de ticket |
| `EstadoTurno` | `EstadoTurno` | Catálogo de estados de turno |
| `Ticket` | `Ticket` | Solicitud de atención de una persona |
| `Turno` | `Turno` | Turno individual dentro de un ticket |
| `LlamadaTurno` | `LlamadaTurno` | Historial de llamadas y re-llamadas (auditoría) |
| `TurnoHistorialDerivacion` | `TurnoHistorialDerivacion` | Historial de derivaciones entre operadores |
| `ConfiguracionArea` | `ConfiguracionArea` | Parámetros operativos por área |
| `ConfiguracionAreaHistorial` | `ConfiguracionAreaHistorial` | Auditoría de cambios de configuración |
| `MotivoCierre` | `MotivoCierre` | Motivos configurables para cerrar un turno |
| `SchemaVersion` | `SchemaVersion` | Control de versiones del esquema SQL |

### Relación Ticket → Turno

Un **Ticket** es la solicitud de atención de una persona para un área. Cada ticket puede tener uno o más **Turnos** (por ejemplo, si el ciudadano es derivado a otro operador se genera un nuevo turno dentro del mismo ticket).

---

## Ciclo de Vida de un Turno

```
PENDIENTE (0)
    │
    ├─[operador llama]──→ LLAMANDO (1)
    │                          │
    │                          ├─[ciudadano se presenta]──→ EN_ATENCION (2)
    │                          │                                │
    │                          │                    ┌──────────┼──────────┐
    │                          │                    ↓          ↓          ↓
    │                          │              FINALIZADO  NO_PRESENTO  DERIVADO
    │                          │                  (3)         (4)         (5)
    │                          │
    │                          └─[no se presenta]──→ NO_PRESENTO (4)
    │
    └─[derivado desde otro]──→ PENDIENTE (0)  ← re-entra como nuevo turno
```

**Acciones disponibles para el operador:**
- `llamar` — pasa a LLAMANDO, registra en `LlamadaTurno`
- `rellamar` — re-notifica sin cambiar estado, registra en `LlamadaTurno`
- `iniciar` — pasa a EN_ATENCION
- `finalizar` — pasa a FINALIZADO (requiere motivo de cierre si está configurado)
- `no_presento` — pasa a NO_PRESENTO
- `derivar` — crea un nuevo turno en otro operador, registra en `TurnoHistorialDerivacion`

---

## Roles y Pantallas

### Rol: Público (anónimo)

| Pantalla | URL | Descripción |
|---|---|---|
| Tótem | `/turnos/` | Formulario para solicitar turno. Acepta `?area=<id>` via QR. |
| Confirmación | `/turnos/ok/<pk>/` | Muestra número de turno y posición en la cola. |
| Monitor | `/turnos/monitor/` | Pantalla de sala de espera con turnos llamados. |

### Rol: Operador (grupo `Operador`)

| Pantalla | URL | Descripción |
|---|---|---|
| Panel de mesa | `/atencion/` | Interfaz principal de atención. Muestra turno actual y cola pendiente. |

El operador es redirigido automáticamente a `/atencion/` después del login. Si su usuario no tiene una `Mesa` asignada, el panel opera en modo de solo lectura del área.

### Rol: Director / SuperAdmin

| Pantalla | URL | Descripción |
|---|---|---|
| Dashboard | `/dashboard/` | Estadísticas del día: pendientes, en atención, finalizados, no presentes. |

El director es redirigido automáticamente a `/dashboard/` después del login.

### Flujo post-login

```python
# apps/core/views.py → postlogin()
Director / SuperAdmin  →  /dashboard/
Operador               →  /atencion/
Sin rol válido         →  logout() → /login/
```

---

## Mapa de URLs

```
/                        →  login (redirige)
/login/                  →  Formulario de login
/logout/                 →  Logout
/postlogin/              →  Redirección según rol

/turnos/                 →  Tótem público
/turnos/ok/<pk>/         →  Confirmación de turno
/turnos/monitor/         →  Monitor de sala de espera
/turnos/tramites.json    →  JSON de trámites activos (para SPA)
/turnos/api/config/      →  Configuración del área por defecto
/turnos/api/config/<id>/ →  Configuración de un área específica

/atencion/               →  Panel del operador
/atencion/api/llamar/<id>/      →  Llamar turno
/atencion/api/rellamar/<id>/    →  Re-llamar turno
/atencion/api/iniciar/<id>/     →  Iniciar atención
/atencion/api/finalizar/<id>/   →  Finalizar turno
/atencion/api/no-presento/<id>/ →  Marcar no se presentó
/atencion/api/proximo/          →  Obtener próximo turno
/atencion/api/derivar/<id>/     →  Derivar a otro operador
/atencion/api/operadores/       →  Listar operadores del área

/dashboard/              →  Dashboard administrativo
/dashboard/api/stats/    →  JSON de estadísticas en vivo

/api/personas/buscar/    →  Búsqueda de persona por DNI (DB Aportes)
/api/turnos/emitir/      →  Emitir turno (tótem SPA)
/api/config/             →  Configuración área por defecto
/api/config/<id>/        →  Configuración área específica

/admin/                  →  Django Admin
```

---

## API REST

Todas las rutas bajo `/api/` son públicas (sin autenticación requerida a nivel HTTP) porque operan desde el tótem anónimo. Las rutas bajo `/atencion/api/` requieren login.

### `POST /api/personas/buscar/`

Consulta la base de datos `Aportes` en `sql01` mediante el stored procedure `Will_Busca_Persona_Turnero`.

**Request:**
```json
{ "dni": 12345678 }
```

**Response 200:**
```json
{
  "nombre": "MARÍA",
  "apellido": "SÁNCHEZ",
  "fecha_nacimiento": "15/03/1958",
  "sexo": "F"
}
```

**Response 404:**
```json
{ "detail": "DNI no encontrado" }
```

---

### `POST /api/turnos/emitir/`

Emite un nuevo turno. Si ya existe un turno PENDIENTE o LLAMANDO para ese DNI y área, devuelve el existente sin crear uno nuevo.

**Request:**
```json
{
  "tramite_id": 3,
  "dni": 12345678,
  "es_embarazada": false,
  "es_discapacitado": false
}
```

**Response 200:**
```json
{
  "turno_id": 142,
  "nombre": "MARÍA SÁNCHEZ",
  "tramite": "Consulta General",
  "espera": 5,
  "prioridad": 1
}
```

---

### `GET /api/config/` · `GET /api/config/<area_id>/`

Devuelve la `ConfiguracionArea` del área solicitada (o la primera activa por defecto).

---

## Integración QR

El sistema no genera QR internamente. Los QR se generan externamente (con cualquier generador) codificando la URL del tótem con el parámetro `?area=<id>`.

**Formato de URL:**
```
http://web03/turnos/?area=<IdArea>
```

Cuando el ciudadano escanea el QR, el tótem (`turnero_public`) resuelve el área por el parámetro y pre-filtra los trámites disponibles. Si no se pasa el parámetro, se usa la primera área activa.

**Uso típico:** Imprimir un QR por área/oficina y colocarlo en la entrada o mostrador. El ciudadano escanea con su celular sin necesidad de instalar nada.

---

## Prioridades Automáticas

El sistema calcula automáticamente la prioridad del turno según la configuración del área (`ConfiguracionArea`).

| Nivel | Descripción | Detección |
|---|---|---|
| 0 | Normal | — |
| 1 | Adulto mayor | Automática: edad ≥ 65 años (calculado desde DNI → Aportes) |
| 2 | Embarazada | Manual: flag `es_embarazada=true` en el formulario |
| 3 | Discapacidad | Manual: flag `es_discapacitado=true` en el formulario |

Los turnos con mayor prioridad aparecen primero en la cola del operador. Cada tipo de prioridad puede habilitarse/deshabilitarse por área desde `ConfiguracionArea`.

---

## Configuración por Área

El modelo `ConfiguracionArea` (tabla `ConfiguracionArea`, `managed=False`) almacena los parámetros operativos de cada área:

| Campo | Por defecto | Descripción |
|---|---|---|
| `permitir_sin_dni` | `False` | Permite emitir turno sin DNI |
| `multiples_turnos_dni` | `True` | Permite más de un turno activo por DNI |
| `max_turnos_por_dia` | `3` | Máximo de turnos por persona cada 24 h |
| `vencimiento_turnos` | `True` | Vence turnos pendientes de días anteriores |
| `prioridad_adulto_mayor` | `True` | Habilita prioridad automática por edad |
| `prioridad_embarazadas` | `True` | Habilita prioridad por embarazo |
| `prioridad_discapacidad` | `True` | Habilita prioridad por discapacidad |
| `emision_hora_inicio` | `07:00` | Desde cuándo se pueden emitir turnos |
| `emision_hora_fin` | `12:30` | Hasta cuándo se pueden emitir turnos |
| `atencion_hora_inicio` | `07:30` | Inicio del horario de atención |
| `atencion_hora_fin` | `12:30` | Fin del horario de atención |
| `permitir_derivaciones` | `False` | Habilita la derivación entre operadores |
| `requiere_motivo_fin` | `True` | Obliga a seleccionar motivo al finalizar turno |
| `tiempo_llamada_seg` | `10` | Duración del overlay de alerta en el monitor |
| `sonido_llamada` | `True` | Reproduce sonido al llamar un turno |
| `media_habilitada` | `False` | Habilita video/imagen institucional en monitor |

---

## Variables de Entorno

El archivo `.env` debe crearse en la raíz del proyecto. **No versionar.**

```env
# Django
SECRET_KEY=<clave-secreta-larga>
DEBUG=False
ALLOWED_HOSTS=web03,<IP-del-servidor>

# Base de datos principal — SQL Server en web03
DB_NAME=Turnero
DB_HOST=web03
SQL_USER=turnero_user
SQL_PASS=<password>
DB_DRIVER=SQL Server Native Client 11.0

# Base de datos Aportes — SQL Server en sql01 (Trusted Connection)
APORTES_DB_HOST=sql01
```

Para generar `SECRET_KEY`:
```cmd
venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Entorno de Desarrollo Local

> Para desarrollo local se puede usar SQLite reemplazando temporalmente `DATABASES` en `settings.py` con `DATABASES_SQLITE`.

```powershell
# 1. Clonar y entrar al proyecto
git clone <repo-url>
cd turnero_django

# 2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt       # dependencias base
pip install -r requirements_websockets.txt  # opcional: channels + daphne

# 4. Crear archivo .env (ver sección Variables de Entorno)
copy .env.example .env   # si existe; sino crear manualmente

# 5. Migraciones (solo para tablas managed=True: MotivoCierre, LlamadaTurno)
python manage.py migrate

# 6. Crear superusuario Django
python manage.py createsuperuser

# 7. Servidor de desarrollo
python manage.py runserver
```

**Nota:** El superusuario de Django (`createsuperuser`) tiene acceso al `/admin/` de Django pero necesita además un registro en la tabla `Usuario` con el mismo `username` y su rol en `UsuarioRol` para que `postlogin` lo redirija correctamente.

---

## Despliegue en Producción (IIS)

El sitio corre como proceso gestionado por **httpPlatformHandler**: IIS delega cada petición HTTP al proceso `uvicorn` que levanta el bat de arranque.

### Parámetros del sitio

| Elemento | Valor |
|---|---|
| Servidor | `web03` |
| App Pool | `AppPool_GestionGestores` |
| Sitio IIS | `Gestion_Gestores` |
| Carpeta física | `C:\inetpub\Sites\Gestion_Gestores` |
| Puerto | `80` |
| Log de arranque | `...\logs\wrapper_stdout.log` |

### Pasos de despliegue

**1. Copiar archivos y preparar entorno:**
```cmd
xcopy /E /I /Y ".\*" "C:\inetpub\Sites\Gestion_Gestores\"
cd C:\inetpub\Sites\Gestion_Gestores
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
mkdir logs
```

**2. Crear `.env` de producción** (ver sección Variables de Entorno).

**3. Recolectar estáticos y verificar:**
```cmd
venv\Scripts\python.exe manage.py collectstatic --noinput
venv\Scripts\python.exe manage.py check --deploy
```

**4. Crear App Pool y sitio IIS (PowerShell como Administrador):**
```powershell
Import-Module WebAdministration

New-WebAppPool -Name "AppPool_GestionGestores"
Set-ItemProperty IIS:\AppPools\AppPool_GestionGestores managedRuntimeVersion ""
Set-ItemProperty IIS:\AppPools\AppPool_GestionGestores startMode AlwaysRunning
Set-WebConfigurationProperty `
    -Filter '/system.applicationHost/applicationPools/add[@name="AppPool_GestionGestores"]' `
    -Name "processModel.idleTimeout" -Value "00:00:00"

New-Website -Name "Gestion_Gestores" `
            -PhysicalPath "C:\inetpub\Sites\Gestion_Gestores" `
            -ApplicationPool "AppPool_GestionGestores" `
            -Port 80 -Force

icacls "C:\inetpub\Sites\Gestion_Gestores" `
    /grant "IIS AppPool\AppPool_GestionGestores:(OI)(CI)M" /T
```

### Archivos de configuración IIS

- **`web.config`** — Define el handler `httpPlatformHandler` con `path="*"` y delega la ejecución a `start_uvicorn.bat`.
- **`start_uvicorn.bat`** — Activa el venv, carga el `.env`, e inicia uvicorn en el puerto que IIS asigna vía `%HTTP_PLATFORM_PORT%`.

### Reiniciar el sitio

```powershell
# Reciclar el App Pool (recarga el proceso uvicorn)
Restart-WebAppPool -Name "AppPool_GestionGestores"

# O desde IIS Manager → App Pools → AppPool_GestionGestores → Recycle
```

### Diagnóstico de problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| IIS devuelve 404 | Handler de `StaticFile` toma precedencia | Agregar `<clear />` antes del `<add>` en `<handlers>` en `web.config` |
| IIS descarga el `.bat` | `httpPlatformHandler` no está instalado | Instalar desde Web Platform Installer |
| 500 en arranque | Error en `.env` o en el `settings.py` | Revisar `logs\wrapper_stdout.log` |
| Estáticos no cargan | `collectstatic` no ejecutado | Ejecutar `manage.py collectstatic` |

---

## Base de Datos

### Base principal — `Turnero` (web03)

Contiene las 18+ tablas del sistema. Todas las migraciones Django sobre estas tablas están deshabilitadas (`managed=False`). El esquema se gestiona con los scripts en `scripts/`.

La base de datos fue migrada desde SQLite a SQL Server 2014. Ver [ESTADO_MIGRACION.md](ESTADO_MIGRACION.md) para el detalle de tablas y datos maestros insertados.

### Base secundaria — `Aportes` (sql01)

Usada exclusivamente para búsqueda de personas por DNI a través del stored procedure:

```sql
EXEC Will_Busca_Persona_Turnero @dni = '12345678'
-- Retorna: apeynom, fecha_nac, sexo
```

La conexión usa **Trusted Connection** (autenticación Windows integrada). No requiere usuario/contraseña en el `.env` más allá del host.

### Tablas managed=True (gestionadas por Django)

| Tabla | Descripción |
|---|---|
| `LlamadaTurno` | Registro de llamadas/re-llamadas (auditoría) |
| `MotivoCierre` | Motivos de cierre configurables desde `/admin/` |

Estas son las únicas tablas que Django crea/altera con `manage.py migrate`.

---

## WebSockets (Tiempo Real)

> El sistema **no usa WebSockets en producción**. El monitor y el panel del operador actualizan mediante **HTTP polling cada 5 segundos** (`setInterval + fetch`). Los archivos de Channels no están cargados en ningún template.

### Implementación actual (polling)

| Pantalla | Mecanismo | Intervalo |
|---|---|---|
| Monitor (`monitor.html`) | `fetch(monitorUrl)` + DOM diff selectivo | 5 s |
| Panel operador (`panel.html`) | `fetch(panelUrl)` + reemplazo de secciones | 5 s |

El polling se pausa automáticamente cuando la pestaña está oculta (`visibilitychange`) y se reanuda al volver.

### Código de WebSocket (no activo)

Los siguientes archivos están escritos pero **no están incluidos en ningún template**:

- `apps/core/consumers.py` — `TurnosConsumer`
- `turnero/routing.py` — ruta `ws/turnos/`
- `static/js/turnos-websocket.js` — cliente JS del monitor
- `static/js/operador-websocket.js` — cliente JS del operador

**Dependencias necesarias si se quisiera activar** (`requirements_websockets.txt`):
```
channels>=4.0.0
channels-redis>=4.1.0
daphne>=4.0.0
```

Activarlo requeriría: instalar Channels + Redis, actualizar `turnero/asgi.py` con el router de Channels, e incluir los `.js` en los templates. No es necesario para el funcionamiento actual.

---

## Estructura de Autenticación

El sistema usa **dos capas de autenticación en paralelo**:

1. **Django Auth** (`django.contrib.auth.User`) — gestiona la sesión HTTP (login/logout/CSRF).
2. **Tabla `Usuario` propia** — contiene datos de perfil y se relaciona con `UsuarioRol` para determinar el rol de la pantalla.

Al hacer login, Django autentica contra su tabla de usuarios. El `postlogin` view luego busca el mismo `username` en la tabla `Usuario` y consulta `UsuarioRol` para decidir la redirección.

> Los usuarios deben existir en **ambas** tablas con el mismo `username`. Crear el usuario Django desde `/admin/` y luego insertar el registro correspondiente en `Usuario` y `UsuarioRol` en SQL Server.
