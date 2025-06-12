from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'      #  ← EXACTO
    label = 'core'          #  etiqueta breve (opcional, pero evita choques)
