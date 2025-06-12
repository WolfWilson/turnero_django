from django.apps import AppConfig


class AtencionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.atencion'      # ← usa ruta completa
    label = 'atencion'          # (opcional, evita choques)
