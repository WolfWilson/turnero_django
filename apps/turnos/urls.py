# apps/turnos/urls.py
from django.urls import path
from . import views

app_name = "turnos"

urlpatterns = [
    path("",             views.turnero_public, name="turnero_public"),
    path("ok/<int:pk>/", views.confirmacion,  name="confirmacion"),
    path("monitor/",     views.monitor,       name="monitor"),
]
