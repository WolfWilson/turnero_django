"""
Utilidades para emitir eventos WebSocket cuando hay cambios en los turnos
Debe llamarse desde las vistas cuando se crean, actualizan o finalizan turnos
"""

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
import json


def emitir_turno_creado(turno):
    """
    Emite un evento cuando se crea un nuevo turno
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    
    async_to_sync(channel_layer.group_send)(
        'turnos_updates',
        {
            'type': 'turno_creado',
            'turno': serializar_turno(turno),
            'timestamp': timezone.now().isoformat()
        }
    )


def emitir_turno_llamado(turno, mesa=None):
    """
    Emite un evento cuando se llama a un turno
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    
    async_to_sync(channel_layer.group_send)(
        'turnos_updates',
        {
            'type': 'turno_llamado',
            'turno': serializar_turno(turno),
            'mesa': {'id': mesa.id, 'nombre': mesa.nombre} if mesa else None,
            'timestamp': timezone.now().isoformat()
        }
    )


def emitir_turno_atendiendo(turno, mesa=None):
    """
    Emite un evento cuando un turno pasa a atención
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    
    async_to_sync(channel_layer.group_send)(
        'turnos_updates',
        {
            'type': 'turno_atendiendo',
            'turno': serializar_turno(turno),
            'mesa': {'id': mesa.id, 'nombre': mesa.nombre} if mesa else None,
            'timestamp': timezone.now().isoformat()
        }
    )


def emitir_turno_finalizado(turno, motivo=None):
    """
    Emite un evento cuando se finaliza un turno
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    
    async_to_sync(channel_layer.group_send)(
        'turnos_updates',
        {
            'type': 'turno_finalizado',
            'turno': serializar_turno(turno),
            'motivo': motivo,
            'timestamp': timezone.now().isoformat()
        }
    )


def emitir_turno_no_presento(turno):
    """
    Emite un evento cuando se marca un turno como no presentado
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    
    async_to_sync(channel_layer.group_send)(
        'turnos_updates',
        {
            'type': 'turno_no_presento',
            'turno': serializar_turno(turno),
            'timestamp': timezone.now().isoformat()
        }
    )


def emitir_turno_actualizado(turno, cambios=None):
    """
    Emite un evento cuando se actualiza un turno
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    
    async_to_sync(channel_layer.group_send)(
        'turnos_updates',
        {
            'type': 'turno_actualizado',
            'turno': serializar_turno(turno),
            'cambios': cambios or {},
            'timestamp': timezone.now().isoformat()
        }
    )


def serializar_turno(turno):
    """
    Convierte un objeto Turno a un diccionario para enviar por WebSocket
    """
    try:
        return {
            'id': turno.id,
            'numero_visible': turno.numero_visible,
            'estado_id': turno.estado_id,
            'estado_nombre': turno.estado.nombre if turno.estado else None,
            'persona_nombre': turno.ticket.persona.nombre_completo if turno.ticket and turno.ticket.persona else None,
            'tramite_id': turno.tramite_id,
            'tramite_nombre': turno.tramite.nombre if turno.tramite else None,
            'area_id': turno.area_id,
            'area_nombre': turno.area.nombre if turno.area else None,
            'mesa_id': turno.mesa_asignada_id,
            'mesa_nombre': turno.mesa_asignada.nombre if turno.mesa_asignada else None,
            'prioridad': turno.ticket.prioridad if turno.ticket else 0,
            'fecha_hora_creacion': turno.fecha_hora_creacion.isoformat() if turno.fecha_hora_creacion else None,
        }
    except Exception as e:
        print(f"Error al serializar turno {turno.id}: {e}")
        return {'id': turno.id, 'error': str(e)}
