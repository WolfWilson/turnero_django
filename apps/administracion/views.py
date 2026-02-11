from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils import timezone
from apps.core.models import Turno, Usuario, UsuarioRol


def es_director(user):
    if user.is_superuser:
        return True
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

    # Pendientes de HOY (emitidos hoy, aún no atendidos)
    pendientes_hoy = Turno.objects.filter(
        estado_id=Turno.PENDIENTE, fecha_turno=hoy
    ).count()

    # Vencidos: pendientes de días anteriores que nunca se atendieron
    pendientes_vencidos = Turno.objects.filter(
        estado_id=Turno.PENDIENTE, fecha_turno__lt=hoy
    ).count()

    stats = {
        "pendientes":         pendientes_hoy,
        "pendientes_vencidos": pendientes_vencidos,
        "en_atencion":        Turno.objects.filter(estado_id=Turno.EN_ATENCION).count(),
        "llamando":           Turno.objects.filter(estado_id=Turno.LLAMANDO).count(),
        "finalizados":        Turno.objects.filter(estado_id=Turno.FINALIZADO, fecha_turno=hoy).count(),
        "no_presento":        Turno.objects.filter(estado_id=Turno.NO_PRESENTO, fecha_turno=hoy).count(),
        "no_presento_total":  Turno.objects.filter(estado_id=Turno.NO_PRESENTO).count(),
    }
    stats["total_hoy"] = (
        pendientes_hoy + stats["en_atencion"] + stats["llamando"]
        + stats["finalizados"] + stats["no_presento"]
    )

    # Turnos recientes (últimos 10 del día, cualquier estado)
    turnos_recientes = (
        Turno.objects.filter(fecha_turno=hoy)
        .select_related('ticket__persona', 'tramite', 'mesa_asignada', 'estado', 'area')
        .order_by('-fecha_hora_creacion')[:10]
    )

    return render(
        request,
        "admin/dashboard_admin.html",
        {"stats": stats, "turnos_recientes": turnos_recientes, "hoy": hoy},
    )
