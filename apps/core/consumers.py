"""
Consumer de WebSockets para actualizaciones en tiempo real de turnos
Utilizado por el Monitor Público y Panel del Operador
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class TurnosConsumer(AsyncWebsocketConsumer):
    """
    Consumer que maneja conexiones WebSocket para actualizaciones de turnos en tiempo real.
    
    Grupos:
    - turnos_updates: Todos los monitores y operadores reciben actualizaciones
    - operador_{user_id}: Canal específico para cada operador
    """
    
    async def connect(self):
        """Se ejecuta cuando un cliente se conecta al WebSocket"""
        self.room_group_name = 'turnos_updates'
        
        # Unirse al grupo de actualizaciones
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Aceptar la conexión
        await self.accept()
        
        # Enviar mensaje de confirmación
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Conectado al sistema de turnos en tiempo real',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        """Se ejecuta cuando un cliente se desconecta"""
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Recibe mensajes del cliente WebSocket
        Esto permite al cliente enviar comandos o solicitar datos
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            
            # Aquí podrías manejar diferentes tipos de mensajes del cliente
            # Por ahora, solo respondemos con un eco
            await self.send(text_data=json.dumps({
                'type': 'message_received',
                'original_type': message_type,
                'timestamp': timezone.now().isoformat()
            }))
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato de mensaje inválido',
                'timestamp': timezone.now().isoformat()
            }))
    
    # ========================================================================
    # Handlers para diferentes tipos de eventos de turno
    # ========================================================================
    
    async def turno_creado(self, event):
        """Notifica cuando se crea un nuevo turno"""
        await self.send(text_data=json.dumps({
            'type': 'turno_creado',
            'turno': event['turno'],
            'timestamp': event['timestamp']
        }))
    
    async def turno_llamado(self, event):
        """Notifica cuando se llama a un turno"""
        await self.send(text_data=json.dumps({
            'type': 'turno_llamado',
            'turno': event['turno'],
            'mesa': event.get('mesa'),
            'timestamp': event['timestamp']
        }))
    
    async def turno_atendiendo(self, event):
        """Notifica cuando un turno pasa a atención"""
        await self.send(text_data=json.dumps({
            'type': 'turno_atendiendo',
            'turno': event['turno'],
            'mesa': event.get('mesa'),
            'timestamp': event['timestamp']
        }))
    
    async def turno_finalizado(self, event):
        """Notifica cuando se finaliza un turno"""
        await self.send(text_data=json.dumps({
            'type': 'turno_finalizado',
            'turno': event['turno'],
            'motivo': event.get('motivo'),
            'timestamp': event['timestamp']
        }))
    
    async def turno_no_presento(self, event):
        """Notifica cuando marcan un turno como no presentado"""
        await self.send(text_data=json.dumps({
            'type': 'turno_no_presento',
            'turno': event['turno'],
            'timestamp': event['timestamp']
        }))
    
    async def turno_actualizado(self, event):
        """Notifica actualizaciones generales de turno"""
        await self.send(text_data=json.dumps({
            'type': 'turno_actualizado',
            'turno': event['turno'],
            'cambios': event.get('cambios', {}),
            'timestamp': event['timestamp']
        }))
    
    async def stats_actualizadas(self, event):
        """Notifica cambios en las estadísticas generales"""
        await self.send(text_data=json.dumps({
            'type': 'stats_actualizadas',
            'stats': event['stats'],
            'timestamp': event['timestamp']
        }))
