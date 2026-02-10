from django.urls import path
from . import views

app_name = "atencion"

urlpatterns = [
    path("", views.panel_mesa, name="panel"),   # /atencion/
]
