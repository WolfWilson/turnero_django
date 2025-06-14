from django.urls import path
from .views import EmitirTurno, BuscarPersona

urlpatterns = [
    path("personas/buscar/", BuscarPersona.as_view(), name="api_buscar_persona"),
    path("turnos/emitir/",   EmitirTurno.as_view(),   name="api_emitir_turno"),
]
