# Monitor UI - Optimización para Televisores

## Resumen de Cambios

Rediseño completo de la interfaz del monitor de turnos, optimizada para pantallas de TV de 32-43" Full HD (1920x1080).

## Características Principales

### 1. Layout Dinámico Inteligente

El monitor ahora ajusta automáticamente su diseño según la cantidad de turnos activos:

- **Sin turnos (modo `solo-video`)**: Video ocupa toda la pantalla con mensaje "En espera de turnos..."
- **1-6 turnos (modo `con-video`)**: Grid 60/40 - Turnos a la izquierda, video a la derecha
- **7+ turnos (modo `sin-video`)**: Turnos ocupan toda la pantalla, video oculto

El cambio entre modos es automático y se ejecuta:
- Cada 5 segundos (verificación periódica)
- Inmediatamente cuando se detectan cambios en el DOM (turnos añadidos/removidos)

### 2. Organización por Estado

Los turnos se muestran agrupados en tres categorías visuales:

#### 🔴 Llamando
- Destacado con animación pulsante
- Color rojo (#F44336)
- Iconos animados
- Efecto de sombra expansivo

#### 🟢 En Atención  
- Color verde (#4CAF50)
- Indica turnos siendo atendidos actualmente
- Muestra número de mesa asignada

#### 🟡 Pendientes
- Color naranja/amarillo (#FF9800)
- Turnos en espera
- Grid más compacto (cards más pequeñas)

### 3. Tarjetas de Turno Consistentes

**Características de las tarjetas:**
- **Tamaño fijo** con overflow controlado
- **Truncado de texto** con `text-overflow: ellipsis`
- **Nombres largos** se cortan con "..." automáticamente
- **Hover effects** sutiles para interactividad (útil en pantallas táctiles)
- **Iconos decorativos** de fondo con transparencia

**Estructura de cada tarjeta:**
```
┌─────────────────────────────────┐
│ A001         Mesa 1             │ ← Header
│                                  │
│ GARCÍA PÉREZ, Juan Pablo        │ ← Persona (truncado)
│ Licencias de Conducir            │ ← Trámite (truncado)
└─────────────────────────────────┘
```

### 4. Header Informativo

El header del monitor incluye:
- **Nombre del área** (grande, destacado)
- **Contador de turnos** activos en tiempo real
- **Reloj** actualizado cada segundo (formato 24h)

### 5. Paleta de Colores Moderna

Esquema oscuro profesional:
- **Background primario**: `#0a1929` (azul marino oscuro)
- **Background secundario**: `#0d1f2d` (azul marino)
- **Acento primario**: `#3ec0ff` (azul cyan brillante)
- **Acento peligro**: `#f44336` (rojo)
- **Acento éxito**: `#4caf50` (verde)
- **Acento advertencia**: `#ff9800` (naranja)

### 6. Animaciones Suaves

- **Entrada de tarjetas**: `slideUp` (500ms)
- **Transiciones de layout**: `600ms ease-in-out`
- **Pulsos en turnos llamando**: Animación infinita a 2s
- **Flash de actualización**: 6 pulsaciones en 3s

## Archivos Modificados

### CSS
- **`static/css/monitor.css`** (643 líneas)
  - Variables CSS para tematización
  - Sistema de grid responsive
  - Estilos de tarjetas con variantes
  - Media queries para diferentes resoluciones
  - Animaciones y transiciones

### JavaScript
- **`static/js/monitor/layout-manager.js`** (NUEVO)
  - Clase `MonitorLayoutManager`
  - Detección automática de cantidad de turnos
  - MutationObserver para cambios del DOM
  - Actualización de reloj
  - Logging para debugging

### HTML
- **`templates/turnos/monitor.html`**
  - Header con área, contador y reloj
  - Grid dinámico con classes condicionales
  - Secciones separadas (turnos, video)
  - Grupos de turnos por estado
  - Script tag para layout-manager.js

## Sistema de Clases CSS

### Grid Principal
```css
.monitor-grid              /* Base: 1 columna (full width) */
.monitor-grid.con-video    /* 2 columnas: 60% / 40% */
.monitor-grid.solo-video   /* Video full screen, turnos ocultos */
```

### Tarjetas
```css
.turno-card                /* Base card */
.turno-llamando            /* Variante: siendo llamado */
.turno-atencion            /* Variante: en atención */
.turno-pendiente           /* Variante: en espera */
```

### Estados
```css
.empty-state               /* Mensaje cuando no hay turnos */
.flash-animation           /* Animación de actualización */
```

## Comportamiento del Layout Manager

### Inicialización
```javascript
// Se crea automáticamente al cargar el DOM
window.layoutManager = new MonitorLayoutManager();
```

### API Pública
```javascript
// Forzar actualización del layout
window.layoutManager.forceUpdate();

// Ver estado actual
window.debugLayout(); // console.table con info del estado
```

### Eventos Detectados
- Adición de nuevas tarjetas de turno
- Remoción de tarjetas de turno
- Cambios en clases de elementos
- Cambios en atributos de datos

## Optimizaciones para TV

### Resoluciones Soportadas
- **1920x1080 (Full HD)**: Diseño principal
- **1600x900**: Grid ajustado (cards 240px mín)
- **1366x768**: Fuentes más pequeñas
- **<1024px**: Video oculto, solo turnos

### Tipografía Responsive
- Sistema de `clamp()` para escalado fluido
- Números de turno: 1.8rem - 2.2rem
- Nombres: 1.2rem - 1.4rem
- Headers: 1.5rem - 2rem

### Performance
- **CSS Grid** nativo para layout (hardware accelerated)
- **MutationObserver** con debouncing implícito
- **RequestAnimationFrame** para cambios de clase
- **Transiciones GPU-accelerated** (transform, opacity)

## Integración con WebSocket

El layout manager está preparado para trabajar con el sistema WebSocket:

```javascript
// Después de recibir evento WebSocket
socket.on('turno_creado', (data) => {
  // ... agregar turno al DOM ...
  
  // El MutationObserver detectará el cambio y actualizará automáticamente
  // O forzar actualización inmediata:
  window.layoutManager.forceUpdate();
});
```

## Testing Recomendado

### Pruebas Visuales
1. Abrir monitor en TV/pantalla grande: `http://localhost:8000/turnos/monitor/?area=1`
2. Crear turnos uno por uno y observar transiciones
3. Verificar truncado con nombres muy largos
4. Probar con 0, 3, 6, 10, 20 turnos simultáneos

### Pruebas de Responsividad
```javascript
// En consola del navegador
window.debugLayout();  // Ver estado actual
window.layoutManager.turnosActivos;  // Cantidad de turnos
window.layoutManager.currentMode;    // Modo actual
```

### Debugging
- La consola muestra logs cuando cambia el modo
- Los cambios de layout se registran con timestamp
- Errores de elementos faltantes se reportan en consola

## Próximos Pasos Opcionales

### Mejoras Futuras
- [ ] Sonido al llamar turno (beep + voz síntesis)
- [ ] Configuración de thresholds por admin panel
- [ ] Modo nocturno/diurno automático
- [ ] Estadísticas en tiempo real en el header
- [ ] Priorización visual de turnos con prioridad especial

### Personalización por Área
- Colores temáticos por tipo de área
- Logos personalizados en el header
- Videos específicos por área
- Mensajes personalizados de inactividad

## Notas Técnicas

### CSS Variables
Todas las variables están centralizadas en `:root`, lo que permite:
- Cambiar colores globalmente desde un solo lugar
- Crear themes alternativos fácilmente
- Ajustar espaciado y tipografía de forma consistente

### Compatibilidad
- Chrome/Edge 90+: ✅ Totalmente compatible
- Firefox 88+: ✅ Totalmente compatible  
- Safari 14+: ✅ Compatible (revisar backdrop-filter)
- IE11: ❌ No soportado (CSS Grid)

### Accesibilidad
- Alto contraste para lectura a distancia
- Tamaños de fuente grandes
- Íconos con significado semántico
- Estados visuales claros y distintos

---

**Fecha de implementación**: 2025-05-XX
**Versión**: 2.0
**Compatibilidad**: Django 5.2+ / Modern browsers
