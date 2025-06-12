from django.apps import AppConfig


class AdministracionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.administracion'
    label = 'administracion'  # (opcional, evita choques)
    verbose_name = 'Administración'  # (opcional, para mostrar en el admin)
