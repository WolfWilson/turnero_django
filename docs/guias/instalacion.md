# 🛠️ Guía de Instalación

## Requisitos Previos

| Requisito       | Versión Mínima | Recomendada |
|-----------------|----------------|-------------|
| Python          | 3.10           | 3.12+       |
| pip             | 21.0           | Última      |
| Git             | 2.0            | Última      |

## Instalación Paso a Paso

### 1. Clonar el Repositorio

```powershell
git clone <url-del-repositorio>
cd turnero_django
```

### 2. Crear Entorno Virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

Si no existe `requirements.txt`, instalar manualmente:

```powershell
pip install django djangorestframework django-environ django-widget-tweaks
```

### 4. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Generar SECRET_KEY:**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 5. Aplicar Migraciones

```powershell
python manage.py migrate
```

### 6. Crear Datos Iniciales

**Crear superusuario:**
```powershell
python manage.py createsuperuser
```

**Cargar fixture de personas (opcional):**
```powershell
python manage.py loaddata personas
```

### 7. Crear Grupos de Usuario

Acceder al admin de Django (`/admin/`) y crear los grupos:

- **Director** - Acceso al dashboard administrativo
- **Operador** - Acceso al panel de mesa

### 8. Ejecutar Servidor de Desarrollo

```powershell
python manage.py runserver
```

Acceder a: http://127.0.0.1:8000/

## Verificación de la Instalación

| URL                           | Resultado Esperado              |
|-------------------------------|---------------------------------|
| http://127.0.0.1:8000/        | Página de login                 |
| http://127.0.0.1:8000/admin/  | Admin de Django                 |
| http://127.0.0.1:8000/turnos/ | Tótem público                   |
| http://127.0.0.1:8000/turnos/monitor/ | Monitor de turnos       |

## Solución de Problemas

### Error: ModuleNotFoundError

```powershell
pip install <nombre-del-modulo>
```

### Error: No module named 'apps.xxx'

Verificar que `sys.path` incluye la carpeta `apps` en `settings.py`.

### Error: SECRET_KEY not found

Crear archivo `.env` con la variable `SECRET_KEY`.

### Error de migraciones

```powershell
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

## Estructura de Archivos Generados

Después de la instalación:

```
turnero_django/
├── .env                 # Variables de entorno (NO commitear)
├── db.sqlite3           # Base de datos SQLite
├── venv/                # Entorno virtual (NO commitear)
└── staticfiles/         # Archivos estáticos recolectados
```

## Archivos a Ignorar (.gitignore)

```gitignore
# Entorno
.env
venv/
*.pyc
__pycache__/

# Base de datos
db.sqlite3

# Estáticos de producción
staticfiles/

# IDE
.vscode/
.idea/
```
