# 👨‍💻 Guía de Desarrollo

## Estructura del Proyecto

```
turnero_django/
├── api/                  # API REST con DRF
│   ├── serializers.py    # Serializadores
│   ├── urls.py           # Rutas de API
│   └── views.py          # Vistas de API
│
├── apps/                 # Aplicaciones Django
│   ├── core/             # Núcleo del sistema
│   │   ├── models.py     # Modelos de datos
│   │   ├── services.py   # Lógica de negocio
│   │   ├── views.py      # Vistas comunes
│   │   └── fixtures/     # Datos de prueba
│   │
│   ├── turnos/           # Gestión de turnos (público)
│   │   ├── forms.py      # Formularios
│   │   ├── services.py   # Servicios de turno
│   │   ├── urls.py       # Rutas
│   │   └── views.py      # Vistas
│   │
│   ├── atencion/         # Panel de operador
│   │   ├── urls.py
│   │   └── views.py
│   │
│   └── administracion/   # Dashboard admin
│       ├── urls.py
│       └── views.py
│
├── templates/            # Plantillas HTML
│   ├── base.html         # Base común
│   ├── base_public.html  # Base para público
│   ├── base_private.html # Base para autenticados
│   ├── admin/            # Templates de admin
│   ├── operador/         # Templates de operador
│   ├── turnos/           # Templates públicos
│   └── partials/         # Componentes reutilizables
│
├── static/               # Archivos estáticos
│   ├── css/              # Estilos
│   ├── js/               # JavaScript
│   └── media/            # Imágenes, videos
│
├── turnero/              # Configuración Django
│   ├── settings.py       # Configuración
│   ├── urls.py           # Rutas principales
│   └── wsgi.py           # WSGI para producción
│
└── docs/                 # Documentación
```

## Convenciones de Código

### Python

- **PEP 8** para estilo de código
- **Type hints** cuando sea útil
- **Docstrings** para funciones públicas
- Nombres en español para modelos de negocio

### Django

- Apps siempre con prefijo `apps.` en INSTALLED_APPS
- Usar `services.py` para lógica de negocio compleja
- Mantener `views.py` delgado (thin views)
- Usar `@login_required` y `@user_passes_test` para acceso

### Templates

- Usar herencia de templates (`{% extends %}`)
- Componentes en `partials/`
- Nombres descriptivos para bloques

### JavaScript

- ES6+ con módulos
- Archivos separados por funcionalidad
- Usar `const` y `let`, evitar `var`

## Flujo de Trabajo

### Crear Nueva Funcionalidad

1. **Crear rama** desde `main`:
   ```bash
   git checkout -b feature/nombre-funcionalidad
   ```

2. **Implementar** siguiendo la estructura:
   - Modelo → `apps/<app>/models.py`
   - Servicio → `apps/<app>/services.py`
   - Vista → `apps/<app>/views.py`
   - Template → `templates/<app>/`

3. **Probar** localmente

4. **Commit** con mensaje descriptivo:
   ```bash
   git commit -m "feat: descripción breve"
   ```

5. **Push** y crear PR

### Mensajes de Commit

```
feat: nueva funcionalidad
fix: corrección de bug
docs: actualización de documentación
style: cambios de formato (sin cambio de lógica)
refactor: refactorización de código
test: añadir o modificar tests
chore: tareas de mantenimiento
```

## Comandos Útiles

### Django

```powershell
# Servidor de desarrollo
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Shell interactivo
python manage.py shell

# Crear superusuario
python manage.py createsuperuser

# Recolectar estáticos
python manage.py collectstatic
```

### Testing

```powershell
# Ejecutar todos los tests
python manage.py test

# Tests de una app
python manage.py test apps.core

# Con verbosidad
python manage.py test -v 2
```

## Agregar Nueva App

1. **Crear la app** dentro de `apps/`:
   ```powershell
   cd apps
   python ../manage.py startapp nueva_app
   ```

2. **Registrar** en `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ...
       'apps.nueva_app',
   ]
   ```

3. **Crear estructura**:
   - `urls.py` con namespace
   - Templates en `templates/nueva_app/`

4. **Incluir URLs** en `turnero/urls.py`:
   ```python
   path("nueva/", include("apps.nueva_app.urls")),
   ```

## Agregar Endpoint API

1. **Crear serializer** en `api/serializers.py`:
   ```python
   class NuevoSerializer(serializers.Serializer):
       campo = serializers.CharField()
   ```

2. **Crear vista** en `api/views.py`:
   ```python
   class NuevoEndpoint(APIView):
       def post(self, request):
           # lógica
           return Response(data)
   ```

3. **Agregar ruta** en `api/urls.py`:
   ```python
   path("nuevo/", NuevoEndpoint.as_view()),
   ```

## Debug

### Django Debug Toolbar

```powershell
pip install django-debug-toolbar
```

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Mensaje de debug")
logger.info("Información")
logger.warning("Advertencia")
logger.error("Error")
```

### Shell Plus (django-extensions)

```powershell
pip install django-extensions
python manage.py shell_plus
```
