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
        print('[WebSocket] ERROR: No hay channel_layer configurado')
        return
    
    turno_data = serializar_turno(turno)
    print(f'[WebSocket] 📞 Emitiendo turno_llamado: Turno {turno.numero_visible} - Mesa {mesa.nombre if mesa else "sin mesa"}')
    
    async_to_sync(channel_layer.group_send)(
        'turnos_updates',
        {
            'type': 'turno_llamado',
            'turno': turno_data,
            'mesa': {'id': mesa.id, 'nombre': mesa.nombre} if mesa else None,
            'timestamp': timezone.now().isoformat()
        }
    )
    print(f'[WebSocket] ✓ Evento turno_llamado emitido correctamente')


def emitir_turno_atendiendo(turno, mesa=None):
    """
    Emite un evento cuando un turno pasa a atención
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        print('[WebSocket] ERROR: No hay channel_layer configurado')
        return
    
    print(f'[WebSocket] ✅ Emitiendo turno_atendiendo: Turno {turno.numero_visible}')
    
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
        print('[WebSocket] ERROR: No hay channel_layer configurado')
        return
    
    print(f'[WebSocket] 🏁 Emitiendo turno_finalizado: Turno {turno.numero_visible}')
    
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
        print('[WebSocket] ERROR: No hay channel_layer configurado')
        return
    
    print(f'[WebSocket] ❌ Emitiendo turno_no_presento: Turno {turno.numero_visible}')
    
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
        # Preparar objeto persona
        persona_data = None
        if turno.ticket and turno.ticket.persona:
            persona_data = {
                'nombre': turno.ticket.persona.nombre,
                'apellido': turno.ticket.persona.apellido,
                'dni': turno.ticket.persona.dni,
                'nombre_completo': turno.ticket.persona.nombre_completo
            }
        
        return {
            'id': turno.id,
            'numero_visible': turno.numero_visible,
            'estado_id': turno.estado_id,
            'estado': turno.estado.nombre if turno.estado else None,
            'persona': persona_data,
            'tramite': turno.tramite.nombre if turno.tramite else None,
            'tramite_id': turno.tramite_id,
            'area': turno.area.nombre if turno.area else None,
            'area_id': turno.area_id,
            'mesa_asignada': turno.mesa_asignada.nombre if turno.mesa_asignada else None,
            'prioridad': turno.ticket.prioridad if turno.ticket else 0,
            'fecha_hora_creacion': turno.fecha_hora_creacion.isoformat() if turno.fecha_hora_creacion else None,
        }
    except Exception as e:
        print(f"Error al serializar turno {turno.id}: {e}")
        return {
            'id': turno.id,
            'numero_visible': getattr(turno, 'numero_visible', '?'),
            'error': str(e)
        }
