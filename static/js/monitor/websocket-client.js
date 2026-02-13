/**
 * WebSocket Integration para Monitor Público
 * Actualiza turnos en tiempo real
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
                console.log('✓ Monitor conectado al sistema de turnos');
                showNotification('Conectado al sistema en tiempo real', 'success');
            },
            
            onDisconnected: function() {
                console.log('✗ Monitor desconectado');
                showNotification('Conexión perdida, intentando reconectar...', 'warning');
            },
            
            onTurnoCreado: function(turno, timestamp) {
                console.log('Nuevo turno creado:', turno);
                // Refrescar lista de pendientes
                recargarTurnos();
            },
            
            onTurnoLlamado: function(turno, mesa, timestamp) {
                console.log('Turno llamado:', turno, 'en mesa:', mesa);
                
                // Mostrar en pantalla con animación
                mostrarTurnoLlamado(turno, mesa);
                
                // Reproducir sonido/voz si está configurado
                if (MONITOR_CONFIG.sonidoLlamada) {
                    reproducirSonidoLlamada();
                }
                
                if (MONITOR_CONFIG.vozLlamada) {
                    anunciarTurnoVoz(turno, mesa);
                }
                
                // Actualizar lista
                setTimeout(recargarTurnos, 500);
            },
            
            onTurnoAtendiendo: function(turno, mesa, timestamp) {
                console.log('Turno en atención:', turno);
                actualizarTurnoEnUI(turno, 'atencion');
            },
            
            onTurnoFinalizado: function(turno, motivo, timestamp) {
                console.log('Turno finalizado:', turno);
                eliminarTurnoDeUI(turno.id);
            },
            
            onTurnoNoPresento: function(turno, timestamp) {
                console.log('Turno no presentó:', turno);
                eliminarTurnoDeUI(turno.id);
            },
            
            onError: function(error) {
                console.error('Error en WebSocket:', error);
            }
        });
    }
    
    /**
     * Muestra un turno llamado con efecto visual
     */
    function mostrarTurnoLlamado(turno, mesa) {
        const container = document.getElementById('turn-container');
        if (!container) return;
        
        // Crear elemento del turno
        const turnoElement = crearElementoTurno(turno, mesa, 'llamando');
        
        // Insertar al inicio con animación
        turnoElement.style.opacity = '0';
        turnoElement.style.transform = 'translateY(-20px)';
        
        container.insertBefore(turnoElement, container.firstChild);
        
        // Animar entrada
        setTimeout(() => {
            turnoElement.style.transition = 'all 0.5s ease';
            turnoElement.style.opacity = '1';
            turnoElement.style.transform = 'translateY(0)';
        }, 10);
        
        // Efecto de flash/pulso
        turnoElement.classList.add('flash-animation');
        setTimeout(() => {
            turnoElement.classList.remove('flash-animation');
        }, 3000);
    }
    
    /**
     * Crea un elemento HTML para un turno
     */
    function crearElementoTurno(turno, mesa, estado) {
        const li = document.createElement('li');
        li.className = `turn-card ${estado === 'llamando' ? 'active' : ''}`;
        li.setAttribute('data-turno-id', turno.id);
        li.setAttribute('data-estado', estado);
        
        const iconMap = {
            'llamando': 'notifications_active',
            'atencion': 'person',
            'pendiente': 'schedule'
        };
        
        const nombre = turno.persona_nombre || `N° ${turno.numero_visible}`;
        const tramite = turno.tramite_nombre || '';
        const mesaNombre = mesa?.nombre || (estado === 'pendiente' ? 'En espera' : '-');
        
        li.innerHTML = `
            <span class="material-icons-outlined bell">${iconMap[estado]}</span>
            <span class="turno">${nombre} | ${tramite}</span>
            <span class="box">${mesaNombre}</span>
        `;
        
        return li;
    }
    
    /**
     * Actualiza un turno existente en la UI
     */
    function actualizarTurnoEnUI(turno, nuevoEstado) {
        const turnoElement = document.querySelector(`[data-turno-id="${turno.id}"]`);
        if (!turnoElement) {
            // Si no existe, refrescar toda la lista
            recargarTurnos();
            return;
        }
        
        // Actualizar clases y estado
        turnoElement.className = `turn-card ${nuevoEstado === 'llamando' ? 'active' : ''}`;
        turnoElement.setAttribute('data-estado', nuevoEstado);
        
        // Actualizar contenido
        const iconMap = {
            'llamando': 'notifications_active',
            'atencion': 'person',
            'pendiente': 'schedule'
        };
        
        const bell = turnoElement.querySelector('.bell');
        if (bell) {
            bell.textContent = iconMap[nuevoEstado];
        }
        
        // Efecto visual de cambio
        turnoElement.style.transition = 'background-color 0.5s ease';
        turnoElement.style.backgroundColor = 'rgba(255, 193, 7, 0.3)';
        setTimeout(() => {
            turnoElement.style.backgroundColor = '';
        }, 1000);
    }
    
    /**
     * Elimina un turno de la UI con animación
     */
    function eliminarTurnoDeUI(turnoId) {
        const turnoElement = document.querySelector(`[data-turno-id="${turnoId}"]`);
        if (!turnoElement) return;
        
        // Animar salida
        turnoElement.style.transition = 'all 0.5s ease';
        turnoElement.style.opacity = '0';
        turnoElement.style.transform = 'translateX(100%)';
        
        setTimeout(() => {
            turnoElement.remove();
            
            // Si no quedan turnos, mostrar mensaje vacío
            const container = document.getElementById('turn-container');
            if (container && container.children.length === 0) {
                container.innerHTML = '<li class="turn-empty">No hay turnos en atención</li>';
            }
        }, 500);
    }
    
    /**
     * Recarga toda la lista de turnos desde el servidor
     */
    function recargarTurnos() {
        // Recargar la página completa o hacer un fetch AJAX
        // Para simplicidad, recargamos
        location.reload();
    }
    
    /**
     * Reproduce sonido de llamada
     */
    function reproducirSonidoLlamada() {
        try {
            const audio = new Audio('/static/media/bell.mp3');
            audio.volume = 0.7;
            audio.play().catch(e => console.log('No se pudo reproducir sonido:', e));
        } catch (error) {
            console.log('Error al reproducir sonido:', error);
        }
    }
    
    /**
     * Anuncia turno por voz
     */
    function anunciarTurnoVoz(turno, mesa) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(
                `Turno ${turno.numero_visible}, dirigirse a ${mesa.nombre}`
            );
            utterance.lang = 'es-ES';
            utterance.rate = 0.9;
            speechSynthesis.speak(utterance);
        }
    }
    
    /**
     * Muestra notificación temporal
     */
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `monitor-notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: rgba(0, 0, 0, 0.85);
            color: white;
            border-radius: 8px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
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
    
})();
