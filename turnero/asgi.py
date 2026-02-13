"""
ASGI config for turnero project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import turnero.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'turnero.settings')

# Inicializar Django ASGI application temprano para asegurar que AppRegistry está poblado
# antes de importar código que pueda importar modelos ORM.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # HTTP tradicional
    "http": django_asgi_app,
    
    # WebSocket handler
    "websocket": AuthMiddlewareStack(
        URLRouter(
            turnero.routing.websocket_urlpatterns
        )
    ),
})
