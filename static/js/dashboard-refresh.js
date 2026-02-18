/**
 * Dashboard Auto-Refresh
 * Actualiza estadísticas cada 60 segundos con animaciones suaves
 */

(function() {
    'use strict';

    const REFRESH_INTERVAL = 60000; // 60 segundos
    const API_ENDPOINT = '/dashboard/api/stats/';
    
    let refreshTimer = null;
    let isUpdating = false;

    /**
     * Actualiza un valor numérico con animación suave
     */
    function updateValueWithAnimation(element, newValue) {
        if (!element) return;
        
        const currentValue = parseInt(element.textContent) || 0;
        
        if (currentValue === newValue) return;
        
        // Cancelar animación previa si existe
        if (element._animInterval) {
            clearInterval(element._animInterval);
            element._animInterval = null;
        }
        
        // Añadir clase de actualización
        element.classList.add('updating');
        
        // Animar el cambio de número
        const duration = 600;
        const steps = 20;
        const stepValue = (newValue - currentValue) / steps;
        const stepDuration = duration / steps;
        
        let currentStep = 0;
        element._animInterval = setInterval(() => {
            currentStep++;
            const intermediateValue = Math.round(currentValue + (stepValue * currentStep));
            element.textContent = intermediateValue;
            
            if (currentStep >= steps) {
                clearInterval(element._animInterval);
                element._animInterval = null;
                element.textContent = newValue;
                element.classList.remove('updating');
                
                // Efecto de "flash" sutil para indicar cambio
                element.classList.add('value-changed');
                setTimeout(() => {
                    element.classList.remove('value-changed');
                }, 1000);
            }
        }, stepDuration);
    }

    /**
     * Mapeo de claves de stats a IDs de elementos en el DOM
     * Nota: en_atencion se maneja por separado (sumado con llamando)
     */
    const statsMapping = {
        'pendientes': 'stat-pendientes',
        'finalizados': 'stat-finalizados',
        'pendientes_vencidos': 'stat-vencidos',
        'no_presento': 'stat-no-presento'
    };

    /**
     * Actualiza las estadísticas del dashboard
     */
    async function refreshStats() {
        if (isUpdating) return;
        
        isUpdating = true;
        
        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const stats = await response.json();
            
            // Actualizar estadísticas simples con animación
            for (const [key, elementId] of Object.entries(statsMapping)) {
                const element = document.getElementById(elementId);
                if (element && stats.hasOwnProperty(key)) {
                    updateValueWithAnimation(element, stats[key]);
                }
            }
            
            // Actualizar en_atencion (incluye llamando) - se maneja aparte
            const enAtencionElement = document.getElementById('stat-en-atencion');
            if (enAtencionElement && stats.en_atencion !== undefined && stats.llamando !== undefined) {
                updateValueWithAnimation(enAtencionElement, stats.en_atencion + stats.llamando);
            }
            
            // Actualizar total_hoy si existe
            const totalElement = document.querySelector('.stat-value[style*="9c27b0"]');
            if (totalElement && stats.total_hoy !== undefined) {
                updateValueWithAnimation(totalElement, stats.total_hoy);
            }
            
            // Actualizar timestamp de última actualización
            updateLastRefreshIndicator();
            
        } catch (error) {
            console.error('Error al actualizar estadísticas:', error);
        } finally {
            isUpdating = false;
        }
    }

    /**
     * Actualiza el indicador de última actualización
     */
    function updateLastRefreshIndicator() {
        const indicator = document.getElementById('last-refresh-time');
        if (indicator) {
            const now = new Date();
            const timeString = now.toLocaleTimeString('es-AR', { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
            });
            indicator.textContent = timeString;
        }
    }

    /**
     * Inicia el sistema de actualización automática
     */
    function startAutoRefresh() {
        // Cancelar timer previo si existe (evitar duplicados)
        stopAutoRefresh();
        
        // Configurar actualización periódica cada 60s
        refreshTimer = setInterval(refreshStats, REFRESH_INTERVAL);
        
        console.log(`✓ Auto-refresh activado: cada ${REFRESH_INTERVAL / 1000}s`);
    }

    /**
     * Detiene el sistema de actualización automática
     */
    function stopAutoRefresh() {
        if (refreshTimer) {
            clearInterval(refreshTimer);
            refreshTimer = null;
        }
    }

    /**
     * Manejo de visibilidad de la página
     * Pausa actualización cuando la pestaña no está visible
     */
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            stopAutoRefresh();
        } else {
            // Al volver, refrescar inmediatamente y reiniciar intervalo
            refreshStats();
            startAutoRefresh();
        }
    });

    // Iniciar cuando el DOM esté listo
    function init() {
        // Establecer hora de carga inicial
        updateLastRefreshIndicator();
        // Iniciar auto-refresh (primer refresh real a los 60s)
        startAutoRefresh();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Exponer funciones globalmente (opcional, para debug)
    window.DashboardRefresh = {
        refresh: refreshStats,
        start: startAutoRefresh,
        stop: stopAutoRefresh
    };

})();
