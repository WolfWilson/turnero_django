from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils import timezone
from apps.core.models import Turno, Usuario, UsuarioRol


def es_director(user):
    try:
        usuario = Usuario.objects.get(username=user.username)
        return UsuarioRol.objects.filter(
            usuario=usuario,
            rol__nombre_rol__in=["Director", "SuperAdmin"],
        ).exists()
    except Usuario.DoesNotExist:
        return False


@login_required
@user_passes_test(es_director)
def dashboard_admin(request):
    """Resumen general para el director."""
    hoy = timezone.localdate()
    stats = {
        "pendientes":   Turno.objects.filter(estado_id=Turno.PENDIENTE).count(),
        "en_atencion":  Turno.objects.filter(estado_id=Turno.EN_ATENCION).count(),
        "finalizados":  Turno.objects.filter(estado_id=Turno.FINALIZADO, fecha_turno=hoy).count(),
    }
    return render(
        request,
        "admin/dashboard_admin.html",
        {"stats": stats},
    )
