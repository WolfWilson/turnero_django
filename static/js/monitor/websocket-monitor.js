/**
 * Cliente WebSocket para Monitor Público
 * Actualiza turnos en tiempo real sin recargas ni parpadeo
 */

(function() {
  'use strict';
  
  let socket = null;
  let reconnectAttempts = 0;
  const MAX_RECONNECT_ATTEMPTS = 5;
  
  /**
   * Inicializa la conexión WebSocket
   */
  function initWebSocket() {
    try {
      socket = new TurnosWebSocket({
        debug: true,
        onConnected: () => {
          console.log('[Monitor] ✅ Conectado al sistema de turnos');
          mostrarNotificacion('Conectado en tiempo real', 'success');
          reconnectAttempts = 0;
        },
        onDisconnected: () => {
          console.log('[Monitor] ❌ Desconectado');
          mostrarNotificacion('Conexión perdida', 'warning');
        },
        onError: (error) => {
          console.error('[Monitor] Error:', error);
        },
        onTurnoCreado: (data) => {
          console.log('[Monitor] Turno creado:', data.turno);
          agregarTurnoPendiente(data.turno);
        },
        onTurnoLlamado: (data) => {
          console.log('[Monitor] 📞 Turno llamado:', data.turno);
          mostrarTurnoLlamado(data.turno, data.mesa);
          
          // Reproducir sonido/voz según configuración
          if (MONITOR_CONFIG.sonidoLlamada) {
            reproducirSonido();
          }
          if (MONITOR_CONFIG.vozLlamada) {
            anunciarVoz(data.turno, data.mesa);
          }
        },
        onTurnoAtendiendo: (data) => {
          console.log('[Monitor] Turno en atención:', data.turno);
          moverTurnoASeccion(data.turno, 'atencion');
        },
        onTurnoFinalizado: (data) => {
          console.log('[Monitor] Turno finalizado:', data.turno);
          eliminarTurno(data.turno.id);
        },
        onTurnoNoPresento: (data) => {
          console.log('[Monitor] No se presentó:', data.turno);
          eliminarTurno(data.turno.id);
        }
      });
      
    } catch (error) {
      console.error('[Monitor] Error al inicializar WebSocket:', error);
      scheduleReconnect();
    }
  }
  
  /**
   * Muestra un turno llamado en la sección correspondiente
   */
  function mostrarTurnoLlamado(turno, mesa) {
    requestAnimationFrame(() => {
      let llamandoGrid = document.querySelector('.llamando-group .turnos-grid');
      
      // Si la sección no existe, crearla dinámicamente
      if (!llamandoGrid) {
        console.warn('[Monitor] ⚠️ Sección llamando-group no existe, creando...');
        crearSeccionDinamica('llamando');
        llamandoGrid = document.querySelector('.llamando-group .turnos-grid');
        if (!llamandoGrid) {
          console.error('[Monitor] ❌ No se pudo crear la sección llamando');
          return;
        }
      }
      
      // Eliminar turno de pendientes si estaba ahí
      const existente = document.querySelector(`[data-turno-id="${turno.id}"]`);
      if (existente) {
        console.log('[Monitor] Turno ya existe en DOM, removiendo de posición anterior...');
        existente.remove();
      }
      
      // Crear tarjeta del turno
      const card = crearTarjetaTurno(turno, mesa, 'llamando');
      
      // Insertar con animación
      card.style.opacity = '0';
      card.style.transform = 'scale(0.9)';
      llamandoGrid.insertBefore(card, llamandoGrid.firstChild);
      
      // Animar entrada
      setTimeout(() => {
        card.style.transition = 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';
        card.style.opacity = '1';
        card.style.transform = 'scale(1)';
      }, 50);
      
      // Forzar actualización del layout manager
      if (window.layoutManager) {
        window.layoutManager.forceUpdate();
      }
    });
  }
  
  /**
   * Crea una sección de turnos si no existe
   */
  function crearSeccionDinamica(seccion) {
    const turnosSection = document.getElementById('turnos-section');
    if (!turnosSection) {
      console.error('[Monitor] No se encontró #turnos-section');
      return;
    }
    
    const titulos = {
      'llamando': '<i class="fas fa-bell"></i> Turnos Llamando Ahora',
      'atencion': '<i class="fas fa-user-check"></i> En Atención',
      'pendientes': '<i class="fas fa-clock"></i> Próximos Turnos'
    };
    
    const groupDiv = document.createElement('div');
    groupDiv.className = `turnos-group ${seccion}-group`;
    groupDiv.innerHTML = `
      <h2 class="group-title">
        ${titulos[seccion] || seccion}
      </h2>
      <div class="turnos-grid"></div>
    `;
    
    // Insertar en orden: llamando > atencion > pendientes
    if (seccion === 'llamando') {
      turnosSection.insertBefore(groupDiv, turnosSection.firstChild);
    } else if (seccion === 'atencion') {
      const llamandoGroup = turnosSection.querySelector('.llamando-group');
      if (llamandoGroup) {
        turnosSection.insertBefore(groupDiv, llamandoGroup.nextSibling);
      } else {
        turnosSection.insertBefore(groupDiv, turnosSection.firstChild);
      }
    } else {
      turnosSection.appendChild(groupDiv);
    }
    
    console.log(`[Monitor] ✅ Sección ${seccion}-group creada`);
  }
  
  /**
   * Crea una tarjeta HTML para un turno
   */
  function crearTarjetaTurno(turno, mesa, tipo) {
    const card = document.createElement('div');
    card.className = `turno-card turno-${tipo}`;
    card.setAttribute('data-turno-id', turno.id);
    
    const personaNombre = turno.persona ? 
      `${turno.persona.apellido}, ${turno.persona.nombre}` : 
      `Turno ${turno.numero_visible}`;
    
    card.innerHTML = `
      <div class="turno-header">
        <span class="turno-numero">${turno.numero_visible}</span>
        <span class="turno-mesa">${mesa ? mesa.nombre : '-'}</span>
      </div>
      <div class="turno-body">
        <div class="turno-persona" title="${personaNombre}">
          ${personaNombre}
        </div>
        <div class="turno-tramite" title="${turno.tramite}">
          ${turno.tramite}
        </div>
      </div>
      <div class="turno-icon">
        <i class="fas fa-${tipo === 'llamando' ? 'bell' : tipo === 'atencion' ? 'user-check' : 'clock'}"></i>
      </div>
    `;
    
    return card;
  }
  
  /**
   * Mueve un turno de una sección a otra
   */
  function moverTurnoASeccion(turno, nuevaSeccion) {
    console.log(`[Monitor] 🔄 Moviendo turno ${turno.numero_visible} (ID: ${turno.id}) a sección: ${nuevaSeccion}`);
    
    requestAnimationFrame(() => {
      const card = document.querySelector(`[data-turno-id="${turno.id}"]`);
      if (!card) {
        console.warn(`[Monitor] ⚠️ Turno ${turno.id} no encontrado en el DOM, agregando directamente a ${nuevaSeccion}`);
        agregarTurnoASeccion(turno, nuevaSeccion);
        return;
      }
      
      console.log(`[Monitor] ✅ Turno ${turno.id} encontrado, moviendo con animación...`);
      
      // Animar salida
      card.style.transition = 'all 0.3s ease';
      card.style.opacity = '0';
      card.style.transform = 'scale(0.9)';
      
      setTimeout(() => {
        card.remove();
        agregarTurnoASeccion(turno, nuevaSeccion);
      }, 300);
    });
  }
  
  /**
   * Agrega un turno a una sección específica
   */
  function agregarTurnoASeccion(turno, seccion) {
    console.log(`[Monitor] 🎯 Agregando turno ${turno.numero_visible} a sección: ${seccion}`);
    
    let grid = document.querySelector(`.${seccion}-group .turnos-grid`);
    
    // Si la sección no existe, crearla dinámicamente
    if (!grid) {
      console.warn(`[Monitor] ⚠️ Sección ${seccion}-group no existe, creando...`);
      crearSeccionDinamica(seccion);
      grid = document.querySelector(`.${seccion}-group .turnos-grid`);
      
      if (!grid) {
        console.error(`[Monitor] ❌ No se pudo crear la sección ${seccion}`);
        return;
      }
    }
    
    // Ocultar empty-state si existe
    const emptyState = document.querySelector('.empty-state');
    if (emptyState) {
      emptyState.remove();
    }
    
    const mesaInfo = turno.mesa_asignada ? { nombre: turno.mesa_asignada } : null;
    const card = crearTarjetaTurno(turno, mesaInfo, seccion);
    
    card.style.opacity = '0';
    grid.insertBefore(card, grid.firstChild);
    
    console.log(`[Monitor] ✅ Turno ${turno.numero_visible} agregado a ${seccion}`);
    
    setTimeout(() => {
      card.style.transition = 'all 0.4s ease';
      card.style.opacity = '1';
    }, 50);
    
    if (window.layoutManager) {
      window.layoutManager.forceUpdate();
    }
  }
  
  /**
   * Agrega un turno pendiente
   */
  function agregarTurnoPendiente(turno) {
    agregarTurnoASeccion(turno, 'pendientes');
  }
  
  /**
   * Elimina un turno del DOM
   */
  function eliminarTurno(turnoId) {
    requestAnimationFrame(() => {
      const card = document.querySelector(`[data-turno-id="${turnoId}"]`);
      if (!card) return;
      
      card.style.transition = 'all 0.3s ease';
      card.style.opacity = '0';
      card.style.transform = 'scale(0.8) translateY(-10px)';
      
      setTimeout(() => {
        const parentGrid = card.closest('.turnos-grid');
        const parentGroup = card.closest('.turnos-group');
        card.remove();
        
        // Si la sección quedó vacía, removerla
        if (parentGrid && parentGrid.children.length === 0 && parentGroup) {
          parentGroup.remove();
          console.log('[Monitor] Sección vacía eliminada');
        }
        
        if (window.layoutManager) {
          window.layoutManager.forceUpdate();
        }
      }, 300);
    });
  }
  
  /**
   * Reproduce sonido de llamada
   */
  function reproducirSonido() {
    try {
      // Intentar usar el elemento audio del template
      const audioEl = document.getElementById('alert-sound');
      if (audioEl && audioEl.src) {
        audioEl.currentTime = 0;
        audioEl.play().catch(() => generarBeep());
        return;
      }
      // Fallback: generar beep con Web Audio API
      generarBeep();
    } catch (error) {
      console.log('[Monitor] Error al reproducir sonido:', error);
    }
  }
  
  function generarBeep() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = 880;
      osc.type = 'sine';
      gain.gain.value = 0.3;
      osc.start();
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
      osc.stop(ctx.currentTime + 0.5);
    } catch (e) {
      // Silenciar - el navegador puede bloquear audio sin interacción
    }
  }
  
  /**
   * Anuncia turno por voz
   */
  function anunciarVoz(turno, mesa) {
    if (!('speechSynthesis' in window)) return;
    
    try {
      const texto = `Turno ${turno.numero_visible}, dirigirse a ${mesa.nombre}`;
      const utterance = new SpeechSynthesisUtterance(texto);
      utterance.lang = 'es-ES';
      utterance.rate = 0.9;
      speechSynthesis.speak(utterance);
    } catch (error) {
      console.log('[Monitor] Error con síntesis de voz:', error);
    }
  }
  
  /**
   * Muestra notificación temporal
   */
  function mostrarNotificacion(mensaje, tipo = 'info') {
    const notif = document.createElement('div');
    notif.className = `monitor-notif monitor-notif-${tipo}`;
    notif.textContent = mensaje;
    notif.style.cssText = `
      position: fixed;
      top: 80px;
      right: 20px;
      padding: 12px 20px;
      background: ${tipo === 'success' ? 'rgba(76, 175, 80, 0.95)' : tipo === 'warning' ? 'rgba(255, 152, 0, 0.95)' : 'rgba(33, 150, 243, 0.95)'};
      color: white;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      z-index: 10000;
      font-weight: 600;
      animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notif);
    
    setTimeout(() => {
      notif.style.animation = 'slideOutRight 0.3s ease';
      setTimeout(() => notif.remove(), 300);
    }, 3000);
  }
  
  /**
   * Programa reconexión
   */
  function scheduleReconnect() {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.error('[Monitor] Máximo de intentos de reconexión alcanzado');
      mostrarNotificacion('No se pudo reconectar. Recargue la página.', 'warning');
      return;
    }
    
    reconnectAttempts++;
    const delay = 3000 * reconnectAttempts;
    
    console.log(`[Monitor] Reintentando en ${delay/1000}s...`);
    setTimeout(() => initWebSocket(), delay);
  }
  
  // Inicializar cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWebSocket);
  } else {
    initWebSocket();
  }
  
  // Limpiar al salir
  window.addEventListener('beforeunload', () => {
    if (socket) {
      socket.disconnect();
    }
  });
  
  // Estilos de animaciones
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideInRight {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(100%); opacity: 0; }
    }
  `;
  document.head.appendChild(style);
  
})();
