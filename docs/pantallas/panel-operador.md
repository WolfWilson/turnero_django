# 👤 Panel del Operador

## Descripción

El **Panel del Operador** es la interfaz que utilizan los empleados de atención al público para gestionar los turnos asignados a su mesa.

## Información Técnica

| Atributo      | Valor                                |
|---------------|--------------------------------------|
| **URL**       | `/mesa/`                             |
| **Vista**     | `apps.atencion.views.panel_mesa`     |
| **Template**  | `templates/operador/panel.html`      |
| **Acceso**    | Requiere login + Grupo `Operador`    |
| **Namespace** | `atencion:panel_mesa`                |

## Control de Acceso

```python
def es_operador(u):
    return u.groups.filter(name="Operador").exists()

@login_required
@user_passes_test(es_operador)
def panel_mesa(request):
    return render(request, "operador/panel.html")
```

## Estructura Visual

```
┌─────────────────────────────────────────────────────────────────┐
│  PANEL DE OPERADOR                              [Salir]         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Bienvenido, Juan                                              │
│  Esta pantalla mostrará tu próximo turno.                      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │              TURNO ACTUAL                               │   │
│  │              ─────────────                              │   │
│  │              [Información del turno]                    │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│       ┌──────────────────┐    ┌──────────────────┐             │
│       │  ▶ LLAMAR       │    │  ✓ FINALIZAR    │             │
│       └──────────────────┘    └──────────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Funcionalidades

### 1. Ver Turno Actual

Muestra información del turno que está siendo atendido o el próximo a llamar:
- Nombre de la persona / Número de ticket
- Categoría
- Tiempo de espera

### 2. Llamar Turno

```
[Botón: Play / Llamar]
```

- Toma el siguiente turno de la cola
- Cambia estado de `PENDIENTE` a `EN_ATENCION`
- Asigna la mesa del operador
- Notifica al monitor público

### 3. Finalizar Atención

```
[Botón: Finalizar]
```

- Cambia estado a `FINALIZADO`
- Registra hora de finalización en `Atencion`
- Libera la mesa para el siguiente turno

## Template Base

El panel hereda de `operador/base_operator.html`:

```html
{% extends "operador/base_operator.html" %}
{% block title %}Panel de Operador{% endblock %}
{% block content %}
  <!-- Contenido del panel -->
{% endblock %}
```

## Flujo de Trabajo

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   LLAMAR    │ ──► │  ATENDIENDO │ ──► │  FINALIZAR  │
│             │     │             │     │             │
│ Turno.pend  │     │ Turno.prog  │     │ Turno.done  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
   Monitor            Monitor             Atencion
   notifica           muestra             registra
```

## Próximas Funcionalidades

- [ ] Ver cola de turnos pendientes
- [ ] Rechazar/Reasignar turno
- [ ] Notas sobre la atención
- [ ] Historial del día
- [ ] Pausar/Reanudar atención
- [ ] Estadísticas personales
