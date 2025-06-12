from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Público
    path("",       include("apps.turnos.urls")),          # /  → tótem   (turnero_public)



    # Zonas privadas
    path("mesa/",      include("apps.atencion.urls")),    # panel operador
    path("dashboard/", include("apps.administracion.urls")),  # admin
]

# Solo en DEBUG se sirven estáticos por Django
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
