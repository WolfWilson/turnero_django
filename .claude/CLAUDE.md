# Turnero Django - Contexto del Proyecto

## 📋 Descripción General

Sistema de gestión de turnos desarrollado en **Django 5.x** con **Django REST Framework** para APIs. Permite la emisión, seguimiento y atención de turnos en una organización con múltiples áreas.

## 🏗️ Arquitectura

### Estructura de Aplicaciones

```
turnero_django/
├── turnero/              # Configuración principal de Django
├── api/                  # API REST con DRF
├── apps/
│   ├── core/             # Modelos centrales (Area, Categoria, Turno, etc.)
│   ├── turnos/           # Tótem público y monitor de turnos
│   ├── atencion/         # Panel del operador
│   └── administracion/   # Dashboard del director/admin
├── templates/            # Plantillas HTML
├── static/               # CSS, JS, media
└── docs/                 # Documentación del proyecto
```

## 👥 Roles de Usuario

| Rol       | Grupo Django | Pantalla Principal          | URL Base     |
|-----------|--------------|-----------------------------| -------------|
| Director  | `Director`   | Dashboard Admin             | `/dashboard/`|
| Operador  | `Operador`   | Panel de Mesa               | `/mesa/`     |
| Público   | (anónimo)    | Tótem/Monitor               | `/turnos/`   |

## 📺 Las 3 Pantallas Principales

### 1. Monitor Público (`/turnos/monitor/`)
- **Template**: `templates/turnos/monitor.html`
- **Vista**: `apps.turnos.views.monitor`
- **Propósito**: Pantalla en sala de espera que muestra los turnos llamados
- **Características**:
  - Lista de turnos del día
  - Reloj en tiempo real
  - Overlay de alertas cuando se llama un turno
  - Reproducción de video institucional

### 2. Panel del Operador (`/mesa/`)
- **Template**: `templates/operador/panel.html`
- **Vista**: `apps.atencion.views.panel_mesa`
- **Requiere**: Login + Grupo `Operador`
- **Propósito**: Interfaz para atender turnos
- **Acciones**:
  - Llamar siguiente turno
  - Finalizar atención
  - Ver turno actual

### 3. Dashboard Admin (`/dashboard/`)
- **Template**: `templates/admin/dashboard_admin.html`
- **Vista**: `apps.administracion.views.dashboard_admin`
- **Requiere**: Login + Grupo `Director`
- **Propósito**: Vista general del sistema
- **Estadísticas**:
  - Turnos pendientes
  - Turnos en atención
  - Turnos finalizados del día

## 📊 Modelos de Datos (apps/core/models.py)

### Entidades Principales

| Modelo             | Descripción                                      |
|--------------------|-------------------------------------------------|
| `Area`             | Oficina o sector de atención                    |
| `AreaAdministrador`| Relación usuario-área para administración       |
| `Categoria`        | Tipo de trámite/consulta dentro de un área      |
| `CategoriaOperador`| Habilitación de operadores por categoría        |
| `Mesa`             | Puesto de atención físico                       |
| `Persona`          | Identificación por DNI                          |
| `Turno`            | Turno emitido (ticket o DNI)                    |
| `Atencion`         | Registro de atención de un turno                |

### Estados del Turno

```python
class Estado(models.TextChoices):
    PENDIENTE   = "pend", "Pendiente"
    EN_ATENCION = "prog", "En atención"
    FINALIZADO  = "done", "Finalizado"
```

### Modos de Turno

```python
class Modo(models.TextChoices):
    NUMERACION = "ticket", "Ticket numerado"
    DNI        = "dni",    "Identificación por DNI"
```

## 🔌 API REST (`/api/`)

| Endpoint               | Método | Descripción                    |
|------------------------|--------|--------------------------------|
| `/api/personas/buscar/`| POST   | Busca persona por DNI          |
| `/api/turnos/emitir/`  | POST   | Emite un nuevo turno           |

## 🔐 Flujo de Autenticación

1. Usuario accede a `/login/`
2. Post-login redirige según grupo:
   - `Director` → `/dashboard/`
   - `Operador` → `/mesa/`
   - Sin grupo válido → logout

## ⚙️ Configuración

- **Base de datos**: SQLite (desarrollo)
- **Zona horaria**: `America/Argentina/Buenos_Aires`
- **Idioma**: `es-ar`
- **Variables de entorno**: `.env` (SECRET_KEY, DEBUG, ALLOWED_HOSTS)

## 🎨 Frontend

- CSS custom en `static/css/`
- JavaScript modular en `static/js/`
- Widget Tweaks para formularios
- Iconos: Material Icons Outlined
- Fuente: Roboto (Google Fonts)

## 📁 Convenciones

- **Apps**: Siempre con prefijo `apps.` en INSTALLED_APPS
- **URLs**: Namespaces por app (`turnos:`, `atencion:`, `administracion:`)
- **Templates**: Estructura por app y rol
- **Servicios**: Lógica de negocio en archivos `services.py`
