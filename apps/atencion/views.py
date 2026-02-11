import json
import logging
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from apps.core.models import Usuario, UsuarioRol, Turno, Mesa, Area, ConfiguracionArea, MotivoCierre
from apps.core import services

logger = logging.getLogger(__name__)


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


def _get_usuario(request):
    """Obtiene el usuario de la tabla Usuario a partir del request Django."""
    try:
        return Usuario.objects.get(username=request.user.username)
    except Usuario.DoesNotExist:
        return None


def _get_mesa_operador(usuario):
    """Obtiene la mesa asignada al operador."""
    return Mesa.objects.filter(operador_asignado=usuario, activa=True).first()


@login_required
@user_passes_test(es_operador)
def panel_mesa(request):
    usuario = _get_usuario(request)
    mesa = _get_mesa_operador(usuario) if usuario else None
    
    # Obtener el área de la mesa del operador
    area = mesa.area if mesa else Area.objects.first()
    config = services.obtener_config_area(area) if area else {}
    horario_atencion = services.esta_en_horario_atencion(area) if area else {'permitido': True, 'mensaje': ''}
    
    # Turno actualmente en atención del operador
    turno_actual = None
    if usuario:
        turno_actual = Turno.objects.filter(
            operador=usuario,
            estado_id__in=[Turno.LLAMANDO, Turno.EN_ATENCION]
        ).select_related('ticket__persona', 'tramite', 'area', 'estado').first()
    
    # Turnos pendientes del área del operador (sin filtrar por fecha,
    # para que se vean los que quedaron pendientes de días anteriores)
    area_filter = {'area': area} if area else {}
    turnos_pendientes = Turno.objects.filter(
        estado_id=Turno.PENDIENTE,
        **area_filter,
    ).select_related(
        'ticket__persona', 'tramite', 'area'
    ).order_by('-ticket__prioridad', 'fecha_hora_creacion')[:15]
    
    # Contar turnos en espera
    total_espera = Turno.objects.filter(
        estado_id=Turno.PENDIENTE,
        **area_filter,
    ).count()
    
    # Motivos de cierre activos para el select del modal
    motivos_cierre = MotivoCierre.objects.filter(activo=True).order_by('orden', 'nombre')
    
    context = {
        'turno_actual': turno_actual,
        'turnos_pendientes': turnos_pendientes,
        'total_espera': total_espera,
        'mesa': mesa,
        'area': area,
        'config': config,
        'config_json': json.dumps(config),  # JSON válido para JS
        'horario_atencion': horario_atencion,
        'motivos_cierre': motivos_cierre,
    }
    
    return render(request, "operador/panel.html", context)


# =====================================================================
#  API ENDPOINTS PARA ACCIONES DEL OPERADOR
# =====================================================================

@login_required
@user_passes_test(es_operador)
@require_POST
def api_llamar_turno(request, turno_id):
    """POST /atencion/api/llamar/<turno_id>/"""
    usuario = _get_usuario(request)
    mesa = _get_mesa_operador(usuario)
    
    if not usuario or not mesa:
        return JsonResponse({'error': 'No tiene mesa asignada'}, status=400)
    
    try:
        turno = Turno.objects.select_related('ticket__persona', 'tramite', 'area', 'estado').get(pk=turno_id)
        turno = services.llamar_turno(turno, usuario, mesa)
        return JsonResponse({
            'ok': True,
            'turno_id': turno.id,
            'estado': turno.estado.nombre,
            'persona': turno.ticket.persona.nombre_completo if turno.ticket.persona else f"N° {turno.numero_visible}",
            'mesa': mesa.nombre,
        })
    except (Turno.DoesNotExist, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def api_iniciar_atencion(request, turno_id):
    """POST /atencion/api/iniciar/<turno_id>/"""
    try:
        turno = Turno.objects.select_related('estado').get(pk=turno_id)
        turno = services.iniciar_atencion(turno)
        return JsonResponse({
            'ok': True,
            'turno_id': turno.id,
            'estado': turno.estado.nombre,
            'hora_inicio': turno.fecha_hora_inicio_atencion.strftime('%H:%M:%S'),
        })
    except (Turno.DoesNotExist, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def api_finalizar_atencion(request, turno_id):
    """POST /atencion/api/finalizar/<turno_id>/
    Body: {
        motivo_cierre_id: int (ID de MotivoCierre),
        prioridad_consulta: int (0=Normal, 1=Abierta, 2=Urgente),
        observaciones: str
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}
    
    motivo_cierre_id = data.get('motivo_cierre_id')
    prioridad_consulta = data.get('prioridad_consulta', 0)
    observaciones = data.get('observaciones') or ''
    observaciones = observaciones.strip() or None
    
    logger.info(f"Finalizando turno {turno_id}: motivo={motivo_cierre_id}, prioridad={prioridad_consulta}, obs={observaciones}")
    
    try:
        turno = Turno.objects.select_related('estado', 'area').get(pk=turno_id)
        turno = services.finalizar_atencion(
            turno,
            motivo_cierre_id=motivo_cierre_id,
            prioridad_consulta=prioridad_consulta,
            observaciones=observaciones
        )
        logger.info(f"Turno {turno_id} finalizado correctamente. Estado: {turno.estado.nombre}")
        return JsonResponse({
            'ok': True,
            'turno_id': turno.id,
            'estado': turno.estado.nombre,
        })
    except (Turno.DoesNotExist, ValueError) as e:
        logger.error(f"Error finalizando turno {turno_id}: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def api_no_presento(request, turno_id):
    """POST /atencion/api/no-presento/<turno_id>/"""
    try:
        turno = Turno.objects.select_related('estado').get(pk=turno_id)
        turno = services.marcar_no_presento(turno)
        return JsonResponse({
            'ok': True,
            'turno_id': turno.id,
            'estado': turno.estado.nombre,
        })
    except (Turno.DoesNotExist, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def api_proximo_turno(request):
    """POST /atencion/api/proximo/"""
    usuario = _get_usuario(request)
    mesa = _get_mesa_operador(usuario)
    
    if not usuario or not mesa:
        return JsonResponse({'error': 'No tiene mesa asignada'}, status=400)
    
    area = mesa.area
    proximo = services.obtener_proximo_turno(area)
    
    if not proximo:
        return JsonResponse({'error': 'No hay turnos pendientes'}, status=404)
    
    try:
        turno = services.llamar_turno(proximo, usuario, mesa)
        return JsonResponse({
            'ok': True,
            'turno_id': turno.id,
            'numero_visible': turno.numero_visible,
            'persona': turno.ticket.persona.nombre_completo if turno.ticket.persona else f"N° {turno.numero_visible}",
            'dni': turno.ticket.persona.dni if turno.ticket.persona else None,
            'tramite': turno.tramite.nombre,
            'mesa': mesa.nombre,
            'prioridad': turno.ticket.prioridad,
        })
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def api_derivar_turno(request, turno_id):
    """POST /atencion/api/derivar/<turno_id>/"""
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}
    
    operador_destino_id = data.get('operador_destino_id')
    motivo = data.get('motivo', '').strip() or None
    
    if not operador_destino_id:
        return JsonResponse({'error': 'Debe indicar el operador destino'}, status=400)
    
    usuario = _get_usuario(request)
    
    try:
        turno = Turno.objects.select_related('estado', 'area').get(pk=turno_id)
        operador_destino = Usuario.objects.get(pk=operador_destino_id)
        turno = services.derivar_turno(turno, usuario, operador_destino, motivo)
        return JsonResponse({
            'ok': True,
            'turno_id': turno.id,
            'derivado_a': operador_destino.display_name,
        })
    except (Turno.DoesNotExist, Usuario.DoesNotExist, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def api_rellamar_turno(request, turno_id):
    """POST /atencion/api/rellamar/<turno_id>/
    
    Re-llama un turno que ya está en estado LLAMANDO.
    Registra un evento de re-llamada que el monitor detectará automáticamente.
    """
    usuario = _get_usuario(request)
    
    try:
        turno = Turno.objects.select_related(
            'estado', 'ticket__persona', 'mesa_asignada', 'tramite'
        ).get(pk=turno_id)
        
        # Llamar al servicio que registra la re-llamada
        services.rellamar_turno(turno, usuario)
        
        persona_nombre = turno.ticket.persona.nombre_completo if turno.ticket.persona else f"N° {turno.numero_visible}"
        mesa_nombre = turno.mesa_asignada.nombre if turno.mesa_asignada else '-'
        
        return JsonResponse({
            'ok': True,
            'turno_id': turno.id,
            'persona': persona_nombre,
            'mesa': mesa_nombre,
            'tramite': turno.tramite.nombre,
        })
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Turno.DoesNotExist:
        return JsonResponse({'error': 'Turno no encontrado'}, status=404)
    except Exception as e:
        logger.error(f"Error en rellamar turno: {e}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
