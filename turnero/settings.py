#turnero/settings.py
from pathlib import Path
import environ, os, sys

BASE_DIR = Path(__file__).resolve().parent.parent
# 2) Cargar .env
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')
# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# ► Añade la carpeta apps al path
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
#  └── debe ir antes de INSTALLED_APPS

# Application definition

INSTALLED_APPS = [
    # Django Channels (debe ir primero para override runserver)
    'daphne',
    
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Propias  ← usa siempre el prefijo apps.
    'apps.core',
    'apps.turnos',
    'apps.atencion',
    'apps.administracion',

    "rest_framework",
    "api",
    "widget_tweaks",
    
    # Channels
    'channels',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'turnero.urls'

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],   # ← añade esta línea
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/login/"


WSGI_APPLICATION = 'turnero.wsgi.application'

# ============================================================
# CHANNELS - Configuración WebSockets
# ============================================================
ASGI_APPLICATION = 'turnero.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        # Usar InMemoryChannelLayer para desarrollo (no requiere Redis)
        # Para producción, cambiar a RedisChannelLayer
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Para producción con Redis, descomentar:
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# SQLite (desarrollo local)
DATABASES_SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# SQL Server (producción)
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': env('DB_NAME'),
        'USER': env('SQL_USER'),
        'PASSWORD': env('SQL_PASS'),
        'HOST': env('DB_HOST'),
        'PORT': '',
        'OPTIONS': {
            'driver': env('DB_DRIVER'),
            'extra_params': 'TrustServerCertificate=yes',
        },
    },
    # Base de datos Aportes para búsqueda de personas
    'aportes': {
        'ENGINE': 'mssql',
        'NAME': 'Aportes',
        'HOST': env('APORTES_DB_HOST'),
        'PORT': '',
        'OPTIONS': {
            'driver': env('DB_DRIVER'),
            'extra_params': 'TrustServerCertificate=yes;Trusted_Connection=yes',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# --- Archivos estáticos ---
STATIC_URL = "static/"            # ya lo tenés
STATICFILES_DIRS = [              # directorios de desarrollo
    BASE_DIR / "static",
]
# Cuando vayas a producción recolectarás en STATIC_ROOT
STATIC_ROOT = BASE_DIR / "staticfiles"   # p.ej. para collectstatic


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
