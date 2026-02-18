/**
 * Monitor Layout Manager
 * Maneja el cambio dinámico entre modos: con-video, solo-video
 * Optimizado para pantallas de TV Full HD (1920x1080)
 */

class MonitorLayoutManager {
  constructor() {
    this.monitorGrid = document.getElementById('monitor-grid');
    this.mediaSection = document.querySelector('.media-section');
    this.turnosSection = document.querySelector('.turnos-section');
    
    // Referencias a grupos de turnos
    this.llamandoGroup = document.querySelector('.llamando-group');
    this.atencionGroup = document.querySelector('.atencion-group');
    this.pendientesGroup = document.querySelector('.pendientes-group');
    
    // Contadores
    this.turnosCounter = document.querySelector('.turnos-counter span:first-of-type');
    
    // Estado actual
    this.currentMode = 'solo-video';
    this.turnosActivos = 0;
    
    // Configuración
    this.checkInterval = 5000; // Revisar cada 5 segundos
    this.transitionDuration = 600; // Duración de la transición (ms)
    
    this.init();
  }
  
  /**
   * Inicializa el manager
   */
  init() {
    console.log('[LayoutManager] Inicializando...');
    
    // Verificación inicial ÚNICA
    requestAnimationFrame(() => {
      this.updateLayout();
    });
    
    // NO MÁS VERIFICACIONES PERIÓDICAS - Solo WebSocket actualiza el layout
    // Esto elimina el parpadeo completamente
    
    // Actualizar reloj cada segundo (esto NO causa parpadeo)
    this.updateClock();
    setInterval(() => {
      this.updateClock();
    }, 1000);
  }
  
  /**
   * Cuenta el número total de turnos activos
   */
  countTurnos() {
    const llamando = this.llamandoGroup?.querySelectorAll('.turno-card:not(.empty-state)').length || 0;
    const atencion = this.atencionGroup?.querySelectorAll('.turno-card:not(.empty-state)').length || 0;
    const pendientes = this.pendientesGroup?.querySelectorAll('.turno-card:not(.empty-state)').length || 0;
    
    return llamando + atencion + pendientes;
  }
  
  /**
   * Actualiza el layout según la cantidad de turnos
   */
  updateLayout() {
    const newCount = this.countTurnos();
    
    // Solo actualizar contador si cambió (evita parpadeo)
    if (newCount !== this.turnosActivos) {
      this.turnosActivos = newCount;
      if (this.turnosCounter) {
        this.turnosCounter.textContent = this.turnosActivos;
      }
    }
    
    const newMode = this.determineMode();
    
    if (newMode !== this.currentMode) {
      console.log(`[LayoutManager] Cambiando de "${this.currentMode}" a "${newMode}"`);
      this.switchMode(newMode);
    }
  }
  
  /**
   * Determina el modo apropiado según la cantidad de turnos
   */
  determineMode() {
    if (this.turnosActivos === 0) {
      return 'solo-video'; // Solo video cuando no hay turnos
    } else if (this.turnosActivos <= 6) {
      return 'con-video'; // Mostrar video y turnos para pocos turnos
    } else {
      return 'sin-video'; // Solo turnos cuando hay muchos
    }
  }
  
  /**
   * Cambia el modo del layout
   */
  switchMode(newMode) {
    if (!this.monitorGrid) {
      console.error('[LayoutManager] No se encontró monitor-grid');
      return;
    }
    
    // Remover clases anteriores
    this.monitorGrid.classList.remove('solo-video', 'con-video', 'sin-video');
    
    // Agregar nueva clase con animación suave
    requestAnimationFrame(() => {
      this.monitorGrid.classList.add(newMode);
      this.currentMode = newMode;
      
      // Callback para analíticas o logging
      this.onModeChanged(newMode);
    });
  }
  
  /**
   * Callback cuando cambia el modo
   */
  onModeChanged(mode) {
    console.log(`[LayoutManager] Modo activo: ${mode} (${this.turnosActivos} turnos)`);
    
    // Ocultar/mostrar elementos según el modo
    if (mode === 'solo-video') {
      this.showInactivityMessage();
    } else {
      this.hideInactivityMessage();
    }
  }
  
  /**
   * Muestra mensaje de inactividad
   */
  showInactivityMessage() {
    const overlay = document.querySelector('.media-overlay');
    const mensaje = document.querySelector('.mensaje-pantalla');
    
    if (overlay && mensaje) {
      overlay.style.display = 'flex';
      mensaje.textContent = 'En espera de turnos...';
    }
  }
  
  /**
   * Oculta mensaje de inactividad
   */
  hideInactivityMessage() {
    const overlay = document.querySelector('.media-overlay');
    if (overlay) {
      overlay.style.display = 'none';
    }
  }
  
  /**
   * Actualiza el reloj del header
   */
  updateClock() {
    const clockElement = document.getElementById('clock');
    if (!clockElement) return;
    
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    
    clockElement.textContent = `${hours}:${minutes}:${seconds}`;
  }
  
  /**
   * Manejo manual del layout (para uso desde WebSocket)
   */
  forceUpdate() {
    console.log('[LayoutManager] Actualización forzada del layout');
    this.updateLayout();
  }
  
  /**
   * Obtiene el estado actual
   */
  getState() {
    return {
      mode: this.currentMode,
      turnosActivos: this.turnosActivos,
      timestamp: new Date().toISOString()
    };
  }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  // Crear instancia global
  window.layoutManager = new MonitorLayoutManager();
  
  console.log('[Monitor] Layout Manager inicializado correctamente');
});

// Exponer funciones para uso desde la consola (debugging)
window.debugLayout = () => {
  if (window.layoutManager) {
    console.table(window.layoutManager.getState());
  }
};
