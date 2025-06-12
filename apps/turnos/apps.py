from django.apps import AppConfig


class TurnosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.turnos'
    label = 'turnos'  # (opcional, evita choques)
    verbose_name = 'Turnos'  # (opcional, para mostrar en el admin) 
