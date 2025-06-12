from django.urls import path
from . import views

app_name = "atencion"

urlpatterns = [
    # Vista de operador placeholder (puedes cambiarla cuando implementes lógica)
    path("", views.panel_mesa, name="panel_mesa"),
]
