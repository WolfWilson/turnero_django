from django.urls import path
from . import views

app_name = "atencion"

urlpatterns = [
    path("", views.panel_mesa, name="panel"),   # /atencion/

    # API endpoints para acciones del operador
    path("api/llamar/<int:turno_id>/",     views.api_llamar_turno,     name="api_llamar"),
    path("api/rellamar/<int:turno_id>/",   views.api_rellamar_turno,   name="api_rellamar"),
    path("api/iniciar/<int:turno_id>/",    views.api_iniciar_atencion, name="api_iniciar"),
    path("api/finalizar/<int:turno_id>/",  views.api_finalizar_atencion, name="api_finalizar"),
    path("api/no-presento/<int:turno_id>/", views.api_no_presento,     name="api_no_presento"),
    path("api/proximo/",                   views.api_proximo_turno,    name="api_proximo"),
    path("api/derivar/<int:turno_id>/",    views.api_derivar_turno,    name="api_derivar"),
]
