/**
 * Cliente WebSocket para actualizaciones en tiempo real de turnos
 * Utilizado por Monitor Público y Panel del Operador
 */

class TurnosWebSocket {
    constructor(options = {}) {
        this.options = {
            reconnectInterval: 3000,
            maxReconnectAttempts: 5,
            debug: false,
            onTurnoCreado: null,
            onTurnoLlamado: null,
            onTurnoAtendiendo: null,
            onTurnoFinalizado: null,
            onTurnoNoPresento: null,
            onTurnoActualizado: null,
            onStatsActualizadas: null,
            onConnected: null,
            onDisconnected: null,
            onError: null,
            ...options
        };
        
        this.ws = null;
        this.reconnectAttempts = 0;
        this.reconnectTimeout = null;
        this.isIntentionalClose = false;
        this.isConnected = false;
        
        this.connect();
    }
    
    /**
     * Establece conexión WebSocket
     */
    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/turnos/`;
            
            this.log('Conectando a WebSocket...', wsUrl);
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = (event) => this.onOpen(event);
            this.ws.onmessage = (event) => this.onMessage(event);
            this.ws.onerror = (event) => this.onError(event);
            this.ws.onclose = (event) => this.onClose(event);
            
        } catch (error) {
            this.log('Error al crear WebSocket:', error);
            this.scheduleReconnect();
        }
    }
    
    /**
     * Handler cuando se establece la conexión
     */
    onOpen(event) {
        this.log('✓ WebSocket conectado');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        if (this.options.onConnected) {
            this.options.onConnected();
        }
        
        // Mostrar indicador visual
        this.updateConnectionStatus(true);
    }
    
    /**
     * Handler para mensajes recibidos
     */
    onMessage(event) {
        try {
            const data = JSON.parse(event.data);
            this.log('← Mensaje recibido:', data);
            
            // Despachar según el tipo de mensaje
            switch (data.type) {
                case 'connection_established':
                    this.log('Conexión establecida:', data.message);
                    break;
                    
                case 'turno_creado':
                    if (this.options.onTurnoCreado) {
                        this.options.onTurnoCreado(data.turno, data.timestamp);
                    }
                    break;
                    
                case 'turno_llamado':
                    if (this.options.onTurnoLlamado) {
                        this.options.onTurnoLlamado(data.turno, data.mesa, data.timestamp);
                    }
                    break;
                    
                case 'turno_atendiendo':
                    if (this.options.onTurnoAtendiendo) {
                        this.options.onTurnoAtendiendo(data.turno, data.mesa, data.timestamp);
                    }
                    break;
                    
                case 'turno_finalizado':
                    if (this.options.onTurnoFinalizado) {
                        this.options.onTurnoFinalizado(data.turno, data.motivo, data.timestamp);
                    }
                    break;
                    
                case 'turno_no_presento':
                    if (this.options.onTurnoNoPresento) {
                        this.options.onTurnoNoPresento(data.turno, data.timestamp);
                    }
                    break;
                    
                case 'turno_actualizado':
                    if (this.options.onTurnoActualizado) {
                        this.options.onTurnoActualizado(data.turno, data.cambios, data.timestamp);
                    }
                    break;
                    
                case 'stats_actualizadas':
                    if (this.options.onStatsActualizadas) {
                        this.options.onStatsActualizadas(data.stats, data.timestamp);
                    }
                    break;
                    
                case 'error':
                    this.log('Error del servidor:', data.message);
                    break;
                    
                default:
                    this.log('Tipo de mensaje no manejado:', data.type);
            }
            
        } catch (error) {
            this.log('Error al procesar mensaje:', error);
        }
    }
    
    /**
     * Handler para errores
     */
    onError(event) {
        this.log('✗ Error en WebSocket:', event);
        this.isConnected = false;
        
        if (this.options.onError) {
            this.options.onError(event);
        }
        
        this.updateConnectionStatus(false);
    }
    
    /**
     * Handler cuando se cierra la conexión
     */
    onClose(event) {
        this.log('WebSocket cerrado:', event.code, event.reason);
        this.isConnected = false;
        
        if (this.options.onDisconnected) {
            this.options.onDisconnected(event);
        }
        
        this.updateConnectionStatus(false);
        
        // Reconectar automáticamente si no fue cierre intencional
        if (!this.isIntentionalClose) {
            this.scheduleReconnect();
        }
    }
    
    /**
     * Programa un intento de reconexión
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
            this.log('✗ Máximo de intentos de reconexión alcanzado');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = this.options.reconnectInterval * this.reconnectAttempts;
        
        this.log(`Reintentando conexión en ${delay}ms (intento ${this.reconnectAttempts}/${this.options.maxReconnectAttempts})...`);
        
        this.reconnectTimeout = setTimeout(() => {
            this.connect();
        }, delay);
    }
    
    /**
     * Envía un mensaje al servidor
     */
    send(type, data = {}) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({ type, ...data });
            this.ws.send(message);
            this.log('→ Mensaje enviado:', { type, ...data });
        } else {
            this.log('✗ No se puede enviar mensaje, WebSocket no conectado');
        }
    }
    
    /**
     * Cierra la conexión WebSocket
     */
    disconnect() {
        this.isIntentionalClose = true;
        
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
        }
        
        if (this.ws) {
            this.ws.close();
        }
        
        this.log('WebSocket desconectado intencionalmente');
    }
    
    /**
     * Actualiza indicador visual de conexión
     */
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('ws-status-indicator');
        if (indicator) {
            if (connected) {
                indicator.className = 'ws-status connected';
                indicator.innerHTML = '<i class="fas fa-circle"></i> Conectado';
            } else {
                indicator.className = 'ws-status disconnected';
                indicator.innerHTML = '<i class="fas fa-circle"></i> Desconectado';
            }
        }
    }
    
    /**
     * Logging condicional
     */
    log(...args) {
        if (this.options.debug) {
            console.log('[TurnosWS]', ...args);
        }
    }
    
    /**
     * Obtiene el estado de la conexión
     */
    getConnectionState() {
        if (!this.ws) return 'CLOSED';
        
        switch (this.ws.readyState) {
            case WebSocket.CONNECTING: return 'CONNECTING';
            case WebSocket.OPEN: return 'OPEN';
            case WebSocket.CLOSING: return 'CLOSING';
            case WebSocket.CLOSED: return 'CLOSED';
            default: return 'UNKNOWN';
        }
    }
}

// Exponer globalmente
window.TurnosWebSocket = TurnosWebSocket;
