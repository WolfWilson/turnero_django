# 📺 Monitor Público

## Descripción

El **Monitor Público** es la pantalla que se muestra en la sala de espera para que los ciudadanos puedan ver los turnos que están siendo llamados.

## Información Técnica

| Atributo      | Valor                              |
|---------------|------------------------------------|
| **URL**       | `/turnos/monitor/`                 |
| **Vista**     | `apps.turnos.views.monitor`        |
| **Template**  | `templates/turnos/monitor.html`    |
| **CSS**       | `static/css/monitor.css`           |
| **JS**        | `static/js/monitor/monitor.js`     |
| **Acceso**    | Público (sin autenticación)        |

## Estructura Visual

```
┌─────────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────┐  ┌─────────────────────┐  │
│  │        LISTA DE TURNOS           │  │                     │  │
│  │                                  │  │   VIDEO/IMAGEN      │  │
│  │  🔔  TURNO            HORA  BOX  │  │   INSTITUCIONAL     │  │
│  │  ─────────────────────────────── │  │                     │  │
│  │  • Juan Pérez • Consulta • M1   │  │                     │  │
│  │  • María García • Trámite • M2  │  │                     │  │
│  │  • N° 15 • General • M3         │  │                     │  │
│  │                                  │  │                     │  │
│  └──────────────────────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes

### Header de la Lista

```html
<header class="turn-header">
  <span class="col-bell"></span>
  <span class="col-turno">TURNO</span>
  <time id="clock" aria-label="Hora actual"></time>
  <span class="col-box">BOX</span>
</header>
```

### Tarjeta de Turno

```html
<li class="turn-card active">
  <span class="material-icons-outlined bell">notifications</span>
  <span class="turno">Juan Pérez • Consulta General</span>
  <span class="box">Mesa 1</span>
</li>
```

### Overlay de Alerta

Cuando se llama un turno, aparece un overlay con animación:

```html
<div id="alert-overlay" aria-live="assertive" hidden>
  <div id="alert-wrapper">
    <!-- Contenido dinámico del turno llamado -->
  </div>
</div>
```

## Funcionalidades

### Actualización en Tiempo Real

- El reloj se actualiza cada segundo
- La lista de turnos se refresca periódicamente
- (Futuro) WebSockets para notificaciones push

### Alerta de Turno Llamado

1. Operador llama turno desde su panel
2. Monitor recibe notificación
3. Se muestra overlay con información del turno
4. Sonido de notificación
5. Overlay desaparece después de X segundos

### Visualización

- Muestra los últimos 8 turnos
- Turnos activos resaltados
- Información mostrada:
  - Nombre de persona o número de ticket
  - Categoría del turno
  - Mesa asignada

## Datos Cargados

```python
def monitor(request):
    hoy = timezone.localdate()
    lista = Turno.objects.filter(fecha=hoy).order_by("creado_en")
    return render(request, "turnos/monitor.html", {"turnos": lista})
```

## Estilos

El archivo `monitor.css` define:
- Grid layout responsivo
- Animaciones de entrada/salida
- Estilos de tarjetas de turno
- Overlay de alertas
- Tema visual de sala de espera

## JavaScript

`monitor.js` maneja:
- Reloj en tiempo real
- Polling de turnos
- Animaciones de alertas
- Sonidos de notificación

## Accesibilidad

- `aria-label` en elementos interactivos
- `aria-live="assertive"` para alertas
- Contraste alto para lectura a distancia
- Fuentes grandes y legibles
