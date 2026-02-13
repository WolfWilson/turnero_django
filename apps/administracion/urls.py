from django.urls import path
from . import views

# apps/administracion/urls.py
app_name = "administracion"  # <-- este es el namespace real

from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_admin, name="home"),
    path("api/stats/", views.dashboard_stats_api, name="stats_api"),
]
