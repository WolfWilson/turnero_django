from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from apps.core import views as core_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # login / logout
    path("login/",  auth_views.LoginView.as_view(
        template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(
        next_page="login"), name="logout"),

    # raíz → login
    path("", auth_views.LoginView.as_view(
        template_name="registration/login.html")),

    path("postlogin/", core_views.postlogin, name="postlogin"),

    # público (lanzados desde el dashboard)
    path("turnos/", include("apps.turnos.urls")),

    # zonas privadas
    path("mesa/",      include("apps.atencion.urls")),
    path("dashboard/", include("apps.administracion.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
