"""
Routing de WebSockets para el proyecto
Define las rutas WebSocket disponibles
"""

from django.urls import re_path
from apps.core import consumers

websocket_urlpatterns = [
    # WebSocket para actualizaciones de turnos (Monitor y Operador)
    re_path(r'ws/turnos/$', consumers.TurnosConsumer.as_asgi()),
]
