from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils import timezone
from apps.core.models import Usuario, UsuarioRol, Turno, Mesa


def es_operador(user):
    # Superusers siempre tienen acceso
    if user.is_superuser:
        return True
    
    try:
        usuario = Usuario.objects.get(username=user.username)
        return UsuarioRol.objects.filter(
            usuario=usuario,
            rol__nombre_rol="Operador",
        ).exists()
    except Usuario.DoesNotExist:
        return False


@login_required
@user_passes_test(es_operador)
def panel_mesa(request):
    # Obtener usuario actual de la tabla Usuario
    try:
        usuario = Usuario.objects.get(username=request.user.username)
    except Usuario.DoesNotExist:
        usuario = None
    
    # Turno actualmente en atención del operador
    turno_actual = None
    if usuario:
        turno_actual = Turno.objects.filter(
            operador=usuario,
            estado_id__in=[Turno.LLAMANDO, Turno.EN_ATENCION]
        ).first()
    
    # Turnos pendientes (sin asignar operador)
    turnos_pendientes = Turno.objects.filter(
        estado_id=Turno.PENDIENTE
    ).select_related('ticket__persona', 'tramite', 'area').order_by('orden', 'fecha_hora_creacion')[:10]
    
    # Contar turnos en espera
    total_espera = Turno.objects.filter(estado_id=Turno.PENDIENTE).count()
    
    context = {
        'turno_actual': turno_actual,
        'turnos_pendientes': turnos_pendientes,
        'total_espera': total_espera,
    }
    
    return render(request, "operador/panel.html", context)
