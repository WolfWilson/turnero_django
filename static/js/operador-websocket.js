/**
 * WebSocket Integration para Panel del Operador
 * Actualiza cola de turnos en tiempo real
 */

(function() {
    'use strict';
    
    let turnosWS = null;
    
    /**
     * Inicializa la conexión WebSocket
     */
    function initWebSocket() {
        turnosWS = new TurnosWebSocket({
            debug: true,
            
            onConnected: function() {
                console.log('✓ Operador conectado al sistema de turnos');
                mostrarEstadoConexion(true);
            },
            
            onDisconnected: function() {
                console.log('✗ Operador desconectado');
                mostrarEstadoConexion(false);
            },
            
            onTurnoCreado: function(turno, timestamp) {
                console.log('Nuevo turno creado:', turno);
                
                // Si el turno es para mi área, actualizar cola
                if (esParaMiArea(turno)) {
                    agregarTurnoACola(turno);
                    actualizarContadorEspera(1);
                    mostrarNotificacion('Nuevo turno en cola', 'info');
                }
            },
            
            onTurnoLlamado: function(turno, mesa, timestamp) {
                console.log('Turno llamado:', turno);
                
                // Si es otro operador de mi área, actualizar
                actualizarEstadoTurno(turno.id, 'llamando');
            },
            
            onTurnoAtendiendo: function(turno, mesa, timestamp) {
                console.log('Turno en atención:', turno);
                actualizarEstadoTurno(turno.id, 'atencion');
            },
            
            onTurnoFinalizado: function(turno, motivo, timestamp) {
                console.log('Turno finalizado:', turno);
                eliminarTurnoDeCola(turno.id);
                actualizarContadorEspera(-1);
            },
            
            onTurnoNoPresento: function(turno, timestamp) {
                console.log('Turno no presentó:', turno);
                eliminarTurnoDeCola(turno.id);
                actualizarContadorEspera(-1);
            },
            
            onTurnoActualizado: function(turno, cambios, timestamp) {
                console.log('Turno actualizado:', turno, cambios);
                actualizarTurnoEnLista(turno);
            },
            
            onError: function(error) {
                console.error('Error en WebSocket:', error);
                mostrarNotificacion('Error de conexión', 'error');
            }
        });
    }
    
    /**
     * Verifica si un turno es para el área del operador
     */
    function esParaMiArea(turno) {
        // Usar la configuración global AREA_CONFIG
        if (typeof AREA_CONFIG !== 'undefined' && AREA_CONFIG.area_id) {
            return turno.area_id === AREA_CONFIG.area_id;
        }
        return true; // Por defecto, asumir que sí
    }
    
    /**
     * Agrega un nuevo turno a la cola de pendientes
     */
    function agregarTurnoACola(turno) {
        const colaPendientes = document.getElementById('turnos-pendientes-lista');
        if (!colaPendientes) return;
        
        // Verificar si ya existe
        if (document.querySelector(`[data-turno-id="${turno.id}"]`)) {
            return;
        }
        
        // Crear elemento del turno
        const turnoCard = crearTarjetaTurno(turno);
        
        // Insertar con animación
        turnoCard.style.opacity = '0';
        turnoCard.style.transform = 'translateY(-20px)';
        
        colaPendientes.insertBefore(turnoCard, colaPendientes.firstChild);
        
        // Animar entrada
        setTimeout(() => {
            turnoCard.style.transition = 'all 0.4s ease';
            turnoCard.style.opacity = '1';
            turnoCard.style.transform = 'translateY(0)';
        }, 10);
        
        // Flash de notificación
        turnoCard.classList.add('nuevo-turno-flash');
        setTimeout(() => {
            turnoCard.classList.remove('nuevo-turno-flash');
        }, 2000);
    }
    
    /**
     * Crea una tarjeta HTML para un turno
     */
    function crearTarjetaTurno(turno) {
        const card = document.createElement('div');
        card.className = 'turno-pendiente-card';
        card.setAttribute('data-turno-id', turno.id);
        
        const prioridadBadge = turno.prioridad > 0 
            ? `<span class="badge-prioridad"><i class="fas fa-star"></i> ${turno.prioridad}</span>` 
            : '';
        
        card.innerHTML = `
            <div class="turno-pendiente-header">
                <div class="turno-numero">${turno.numero_visible}</div>
                ${prioridadBadge}
                <div class="turno-hora">${formatearHora(turno.fecha_hora_creacion)}</div>
            </div>
            <div class="turno-pendiente-body">
                <div class="turno-persona">
                    <i class="fas fa-user"></i>
                    ${turno.persona_nombre || 'Sin datos'}
                </div>
                <div class="turno-tramite">
                    <i class="fas fa-briefcase"></i>
                    ${turno.tramite_nombre || ''}
                </div>
            </div>
            <div class="turno-pendiente-footer">
                <button class="btn-llamar-turno" onclick="llamarTurnoDesdeWS(${turno.id})">
                    <i class="fas fa-bell"></i> Llamar
                </button>
            </div>
        `;
        
        return card;
    }
    
    /**
     * Actualiza el estado visual de un turno
     */
    function actualizarEstadoTurno(turnoId, nuevoEstado) {
        const turnoCard = document.querySelector(`[data-turno-id="${turnoId}"]`);
        if (!turnoCard) return;
        
        // Agregar clase de estado
        turnoCard.classList.add(`estado-${nuevoEstado}`);
        
        // Efecto visual de actualización
        turnoCard.style.transition = 'transform 0.3s ease';
        turnoCard.style.transform = 'scale(1.02)';
        setTimeout(() => {
            turnoCard.style.transform = 'scale(1)';
        }, 300);
    }
    
    /**
     * Actualiza información de un turno en la lista
     */
    function actualizarTurnoEnLista(turno) {
        const turnoCard = document.querySelector(`[data-turno-id="${turno.id}"]`);
        if (!turnoCard) return;
        
        // Actualizar contenido sin reemplazar todo el elemento
        const personaElement = turnoCard.querySelector('.turno-persona');
        if (personaElement && turno.persona_nombre) {
            personaElement.innerHTML = `<i class="fas fa-user"></i> ${turno.persona_nombre}`;
        }
        
        // Efecto de actualización
        turnoCard.classList.add('actualizado');
        setTimeout(() => {
            turnoCard.classList.remove('actualizado');
        }, 1000);
    }
    
    /**
     * Elimina un turno de la cola
     */
    function eliminarTurnoDeCola(turnoId) {
        const turnoCard = document.querySelector(`[data-turno-id="${turnoId}"]`);
        if (!turnoCard) return;
        
        // Animar salida
        turnoCard.style.transition = 'all 0.4s ease';
        turnoCard.style.opacity = '0';
        turnoCard.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            turnoCard.remove();
            
            // Si no quedan turnos pendientes, mostrar mensaje
            const colaPendientes = document.getElementById('turnos-pendientes-lista');
            if (colaPendientes && colaPendientes.children.length === 0) {
                colaPendientes.innerHTML = `
                    <div class="cola-vacia">
                        <i class="fas fa-inbox"></i>
                        <p>No hay turnos pendientes</p>
                    </div>
                `;
            }
        }, 400);
    }
    
    /**
     * Actualiza el contador de turnos en espera
     */
    function actualizarContadorEspera(incremento) {
        const contador = document.querySelector('.espera-numero');
        if (!contador) return;
        
        const actual = parseInt(contador.textContent) || 0;
        const nuevo = Math.max(0, actual + incremento);
        
        // Animar cambio
        contador.style.transition = 'transform 0.3s ease';
        contador.style.transform = 'scale(1.2)';
        contador.textContent = nuevo;
        
        setTimeout(() => {
            contador.style.transform = 'scale(1)';
        }, 300);
    }
    
    /**
     * Muestra el estado de conexión
     */
    function mostrarEstadoConexion(conectado) {
        let indicator = document.getElementById('ws-status-indicator');
        
        if (!indicator) {
            // Crear indicador si no existe
            indicator = document.createElement('div');
            indicator.id = 'ws-status-indicator';
            indicator.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 10px 15px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 8px;
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            `;
            document.body.appendChild(indicator);
        }
        
        if (conectado) {
            indicator.className = 'ws-status connected';
            indicator.style.background = 'rgba(76, 175, 80, 0.9)';
            indicator.style.color = 'white';
            indicator.innerHTML = '<i class="fas fa-circle"></i> Conectado';
        } else {
            indicator.className = 'ws-status disconnected';
            indicator.style.background = 'rgba(244, 67, 54, 0.9)';
            indicator.style.color = 'white';
            indicator.innerHTML = '<i class="fas fa-circle"></i> Desconectado';
        }
    }
    
    /**
     * Muestra notificación temporal
     */
    function mostrarNotificacion(mensaje, tipo = 'info') {
        const notification = document.createElement('div');
        notification.className = `operador-notification ${tipo}`;
        
        const colores = {
            'info': 'rgba(33, 150, 243, 0.95)',
            'success': 'rgba(76, 175, 80, 0.95)',
            'warning': 'rgba(255, 193, 7, 0.95)',
            'error': 'rgba(244, 67, 54, 0.95)'
        };
        
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            padding: 15px 20px;
            background: ${colores[tipo] || colores.info};
            color: white;
            border-radius: 8px;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideInRight 0.3s ease;
            max-width: 300px;
        `;
        notification.textContent = mensaje;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    /**
     * Formatea fecha/hora
     */
    function formatearHora(fechaStr) {
        try {
            const fecha = new Date(fechaStr);
            return fecha.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
        } catch {
            return '--:--';
        }
    }
    
    /**
     * Función expuesta para llamar turno desde WebSocket
     */
    window.llamarTurnoDesdeWS = function(turnoId) {
        // Usar la función existente del panel si existe
        if (typeof llamarSiguiente === 'function') {
            llamarSiguiente();
        } else {
            console.log('Llamar turno:', turnoId);
        }
    };
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWebSocket);
    } else {
        initWebSocket();
    }
    
    // Limpiar al salir
    window.addEventListener('beforeunload', () => {
        if (turnosWS) {
            turnosWS.disconnect();
        }
    });
    
    // Exponer globalmente para debugging
    window.operadorWS = {
        getConnection: () => turnosWS,
        reconnect: () => {
            if (turnosWS) turnosWS.disconnect();
            setTimeout(initWebSocket, 1000);
        }
    };
    
})();
