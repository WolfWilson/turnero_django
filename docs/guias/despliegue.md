# 🚀 Guía de Despliegue

## Preparación para Producción

### 1. Configuración de settings.py

```python
# NUNCA en producción
DEBUG = False

# Hosts permitidos
ALLOWED_HOSTS = ['tudominio.com', 'www.tudominio.com']

# SECRET_KEY desde variable de entorno
SECRET_KEY = os.environ.get('SECRET_KEY')
```

### 2. Variables de Entorno (.env)

```env
SECRET_KEY=clave-muy-larga-y-aleatoria-para-produccion
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DATABASE_URL=postgres://user:pass@host:5432/dbname
```

### 3. Base de Datos PostgreSQL

```python
# settings.py
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

**Dependencia:**
```powershell
pip install dj-database-url psycopg2-binary
```

### 4. Archivos Estáticos

```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise para servir estáticos
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Añadir
    # ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**Dependencia:**
```powershell
pip install whitenoise
```

**Recolectar:**
```powershell
python manage.py collectstatic --no-input
```

### 5. Seguridad

```python
# settings.py (producción)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

## Opciones de Despliegue

### Opción A: Servidor Linux + Gunicorn + Nginx

#### Instalar dependencias

```bash
pip install gunicorn
```

#### Archivo Gunicorn (gunicorn.conf.py)

```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
timeout = 120
```

#### Servicio Systemd (/etc/systemd/system/turnero.service)

```ini
[Unit]
Description=Turnero Django
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/turnero
Environment="PATH=/var/www/turnero/venv/bin"
ExecStart=/var/www/turnero/venv/bin/gunicorn turnero.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### Nginx (/etc/nginx/sites-available/turnero)

```nginx
server {
    listen 80;
    server_name tudominio.com;

    location /static/ {
        alias /var/www/turnero/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Opción B: Docker

#### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "turnero.wsgi:application"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
      - DATABASE_URL=postgres://user:pass@db:5432/turnero
    depends_on:
      - db

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=turnero
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

volumes:
  postgres_data:
```

### Opción C: PaaS (Railway, Render, Heroku)

#### Procfile (Heroku/Railway)

```
web: gunicorn turnero.wsgi:application
release: python manage.py migrate
```

#### render.yaml (Render)

```yaml
services:
  - type: web
    name: turnero
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --no-input
    startCommand: gunicorn turnero.wsgi:application
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: False
```

## Checklist de Despliegue

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` configurado como variable de entorno
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] Base de datos PostgreSQL configurada
- [ ] `collectstatic` ejecutado
- [ ] Migraciones aplicadas
- [ ] HTTPS configurado
- [ ] Headers de seguridad activos
- [ ] Logs configurados
- [ ] Backups de base de datos programados
- [ ] Monitoreo configurado

## Monitoreo

### Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/turnero/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
        },
    },
}
```

### Sentry (errores)

```python
pip install sentry-sdk

import sentry_sdk
sentry_sdk.init(
    dsn="tu-dsn-de-sentry",
    traces_sample_rate=1.0,
)
```
