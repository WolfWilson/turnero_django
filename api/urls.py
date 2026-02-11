from django.urls import path
from .views import EmitirTurno, BuscarPersona, ConfiguracionAreaAPI

urlpatterns = [
    path("personas/buscar/", BuscarPersona.as_view(), name="api_buscar_persona"),
    path("turnos/emitir/",   EmitirTurno.as_view(),   name="api_emitir_turno"),
    path("config/",          ConfiguracionAreaAPI.as_view(), name="api_config"),
    path("config/<int:area_id>/", ConfiguracionAreaAPI.as_view(), name="api_config_area"),
]
