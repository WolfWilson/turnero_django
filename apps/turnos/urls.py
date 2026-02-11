# apps/turnos/urls.py
from django.urls import path
from . import views

app_name = "turnos"

urlpatterns = [
    path("",             views.turnero_public, name="turnero_public"),
    path("ok/<int:pk>/", views.confirmacion,  name="confirmacion"),
    path("monitor/",     views.monitor,       name="monitor"),
    path("tramites.json", views.tramites_json, name="tramites_json"),
    path("api/config/",              views.api_config_area, name="api_config"),
    path("api/config/<int:area_id>/", views.api_config_area, name="api_config_area"),
]
