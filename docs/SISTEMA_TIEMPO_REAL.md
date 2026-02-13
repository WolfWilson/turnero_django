# Sistema de Actualizaciones en Tiempo Real

Este documento explica cómo funciona el sistema de actualizaciones implementado en el proyecto turnero.

## Arquitectura Implementada

Se ha implementado una **arquitectura mixta** que optimiza el rendimiento:

### 1. Dashboard del Administrador - Fetch AJAX cada 60s
**Ubicación**: `/dashboard/`

- **Tecnología**: Fetch API + JSON
- **Intervalo**: 60 segundos
- **Endpoint**: `/dashboard/api/stats/`
- **Archivos**:
  - `static/js/dashboard-refresh.js` - Cliente JavaScript
  - `static/css/dashboard.css` - Animaciones CSS
  - `apps/administracion/views.py::dashboard_stats_api` - API endpoint

**Características**:
- ✅ Actualización suave sin parpadeo
- ✅ Animaciones al cambiar valores
- ✅ Se pausa cuando la pestaña está oculta
- ✅ Indicador de última actualización
- ✅ Transiciones CSS para evitar saltos visuales

**Uso**:
```javascript
// Manual (para debugging)
DashboardRefresh.refresh();  // Forzar actualización
DashboardRefresh.stop();     // Detener auto-refresh
DashboardRefresh.start();    // Iniciar auto-refresh
```

---

### 2. Monitor Público y Panel del Operador - WebSockets
**Ubicaciones**: `/turnos/monitor/` y `/operador/panel/`

- **Tecnología**: Django Channels + WebSockets
- **Actualización**: Tiempo real (instantánea)
- **Protocolo**: WS/WSS
- **Archivos**:
  - `apps/core/consumers.py` - Consumer WebSocket
  - `turnero/routing.py` - Routing WebSocket
  - `static/js/turnos-websocket.js` - Cliente base
  - `static/js/monitor/websocket-client.js` - Cliente monitor
  - `static/js/operador-websocket.js` - Cliente operador

**Características**:
- ✅ Actualizaciones instantáneas
- ✅ Reconexión automática (máx 5 intentos)
- ✅ Indicador visual de conexión
- ✅ Notificaciones de eventos
- ✅ Animaciones para nuevos elementos

---

## Configuración

### Settings.py
```python
INSTALLED_APPS = [
    'daphne',  # Debe ir primero
    # ... otros apps
    'channels',
]

ASGI_APPLICATION = 'turnero.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
        # Para producción: usar RedisChannelLayer
    }
}
```

### Para Producción con Redis
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

---

## Emitir Eventos desde el Backend

Cuando ocurre un cambio en un turno, emitir el evento correspondiente:

```python
from apps.core.websocket_utils import (
    emitir_turno_creado,
    emitir_turno_llamado,
    emitir_turno_atendiendo,
    emitir_turno_finalizado,
    emitir_turno_no_presento
)

# Ejemplo: Al crear un turno
turno = Turno.objects.create(...)
emitir_turno_creado(turno)

# Ejemplo: Al llamar un turno
turno.estado_id = Turno.LLAMANDO
turno.save()
emitir_turno_llamado(turno, mesa=turno.mesa_asignada)

# Ejemplo: Al finalizar
turno.estado_id = Turno.FINALIZADO
turno.save()
emitir_turno_finalizado(turno, motivo="Atendido")
```

---

## Eventos WebSocket Disponibles

### Eventos del Servidor → Cliente

| Evento | Descripción | Payload |
|--------|-------------|---------|
| `connection_established` | Conexión establecida | `{message, timestamp}` |
| `turno_creado` | Nuevo turno creado | `{turno, timestamp}` |
| `turno_llamado` | Turno llamado | `{turno, mesa, timestamp}` |
| `turno_atendiendo` | Turno en atención | `{turno, mesa, timestamp}` |
| `turno_finalizado` | Turno finalizado | `{turno, motivo, timestamp}` |
| `turno_no_presento` | No se presentó | `{turno, timestamp}` |
| `turno_actualizado` | Turno modificado | `{turno, cambios, timestamp}` |
| `stats_actualizadas` | Stats actualizadas | `{stats, timestamp}` |

---

## Estructura del Objeto Turno (Serializado)

```javascript
{
  id: 123,
  numero_visible: "A-045",
  estado_id: 1,
  estado_nombre: "Llamando",
  persona_nombre: "Juan Pérez",
  tramite_id: 5,
  tramite_nombre: "Trámite X",
  area_id: 2,
  area_nombre: "Ventanilla",
  mesa_id: 10,
  mesa_nombre: "Mesa 1",
  prioridad: 0,
  fecha_hora_creacion: "2026-02-13T10:30:00"
}
```

---

## Iniciar el Servidor

### Desarrollo (con WebSockets)
```bash
python manage.py runserver
```

Django Channels con `daphne` reemplaza automáticamente el servidor de desarrollo.

### Producción (con Daphne + Nginx)
```bash
# Iniciar Daphne
daphne -b 0.0.0.0 -p 8000 turnero.asgi:application

# Nginx como proxy inverso
# Configurar upgrade de HTTP a WebSocket
```

---

## Testing

### Test Manual del Dashboard
1. Abrir `/dashboard/`
2. Verificar en consola: `✓ Auto-refresh activado: cada 60s`
3. Esperar 60s y observar animación de actualización
4. Crear un turno y verificar que stats se actualicen

### Test Manual de WebSockets
1. Abrir monitor: `/turnos/monitor/`
2. Abrir panel operador: `/operador/panel/`
3. Verificar en ambas consolas: `✓ [TurnosWS] WebSocket conectado`
4. Crear/llamar/finalizar turnos y observar actualizaciones instantáneas

### Debugging
```javascript
// En consola del navegador (Dashboard)
DashboardRefresh.refresh();  // Forzar actualización

// En consola (Monitor/Operador)
operadorWS.getConnection().getConnectionState();  // Ver estado WS
operadorWS.reconnect();  // Forzar reconexión
```

---

## Ventajas de Esta Arquitectura

### Dashboard (Fetch cada 60s)
- ✅ Simple y eficiente
- ✅ No consume recursos cuando no se usa
- ✅ Perfecto para datos que cambian lentamente
- ✅ No requiere conexión persistente

### Monitor/Operador (WebSocket)
- ✅ Actualizaciones instantáneas
- ✅ Experiencia en tiempo real
- ✅ Menos carga en el servidor (un evento vs múltiples polls)
- ✅ Mejor UX para operaciones críticas

---

## Resolución de Problemas

### WebSocket no conecta
1. Verificar que `daphne` está en INSTALLED_APPS
2. Verificar ASGI_APPLICATION en settings
3. Verificar routing.py existe
4. Check consola del navegador para errores

### Dashboard no actualiza
1. Verificar que `/dashboard/api/stats/` responde JSON
2. Verificar en consola: `✓ Auto-refresh activado`
3. Verificar que IDs de elementos existen (stat-pendientes, etc.)

### Eventos no se emiten
1. Verificar que `emitir_turno_*` se llama después de guardar
2. Verificar CHANNEL_LAYERS configurado
3. Para InMemory: solo funciona en un proceso (no multi-worker)
4. Para producción: usar Redis

---

## Próximos Pasos (Opcional)

- [ ] Implementar Redis para producción
- [ ] Agregar autenticación a WebSocket (por usuario/rol)
- [ ] Implementar heartbeat para detectar conexiones muertas
- [ ] Agregar métricas de conexiones activas
- [ ] Implementar rate limiting para prevenir abuse

---

## Referencias

- [Django Channels Docs](https://channels.readthedocs.io/)
- [WebSocket API MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Fetch API MDN](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
