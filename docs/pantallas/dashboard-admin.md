# 📊 Dashboard Administrativo

## Descripción

El **Dashboard Administrativo** es el panel de control para directores y administradores del sistema. Proporciona una vista general del estado de los turnos y acceso a funciones de gestión.

## Información Técnica

| Atributo      | Valor                                        |
|---------------|----------------------------------------------|
| **URL**       | `/dashboard/`                                |
| **Vista**     | `apps.administracion.views.dashboard_admin`  |
| **Template**  | `templates/admin/dashboard_admin.html`       |
| **Acceso**    | Requiere login + Grupo `Director`            |
| **Namespace** | `administracion:home`                        |

## Control de Acceso

```python
def es_director(user):
    return user.groups.filter(name="Director").exists()

@login_required
@user_passes_test(es_director)
def dashboard_admin(request):
    hoy = timezone.localdate()
    stats = {
        "pendientes":   Turno.objects.filter(estado="pend").count(),
        "en_atencion":  Turno.objects.filter(estado="prog").count(),
        "finalizados":  Turno.objects.filter(estado="done", fecha=hoy).count(),
    }
    return render(request, "admin/dashboard_admin.html", {"stats": stats})
```

## Estructura Visual

```
┌─────────────────────────────────────────────────────────────────┐
│  PANEL DE ADMINISTRACIÓN                        [Salir]         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Bienvenido, Director                                          │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  PENDIENTES │  │ EN ATENCIÓN │  │ FINALIZADOS │             │
│  │     12      │  │      3      │  │     45      │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  OPCIONES DEL SISTEMA                                          │
│  ────────────────────                                          │
│  • Ver monitor de turnos                                       │
│  • Totem (turnero público)                                     │
│  • [Salir]                                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Estadísticas Mostradas

| Métrica       | Filtro                                      | Descripción                    |
|---------------|---------------------------------------------|--------------------------------|
| Pendientes    | `estado="pend"`                             | Turnos esperando atención      |
| En Atención   | `estado="prog"`                             | Turnos siendo atendidos ahora  |
| Finalizados   | `estado="done"` + `fecha=hoy`               | Turnos cerrados hoy            |

## Enlaces Disponibles

| Enlace                    | URL                      | Descripción              |
|---------------------------|--------------------------|--------------------------|
| Ver monitor de turnos     | `/turnos/monitor/`       | Pantalla de sala espera  |
| Totem (turnero público)   | `/turnos/`               | Solicitar turno          |

## Template Base

Hereda de `admin/base_admin.html`:

```html
{% extends "admin/base_admin.html" %}
{% block content %}
  <h1>Panel de Administración</h1>
  <!-- Estadísticas y opciones -->
{% endblock %}
```

## Próximas Funcionalidades

### Gestión de Áreas
- [ ] CRUD de áreas
- [ ] Activar/Desactivar áreas
- [ ] Asignar administradores

### Gestión de Categorías
- [ ] CRUD de categorías
- [ ] Asignar operadores a categorías
- [ ] Ordenar prioridades

### Gestión de Mesas
- [ ] CRUD de mesas
- [ ] Ver estado de ocupación
- [ ] Asignar categorías a mesas

### Gestión de Operadores
- [ ] Listar operadores por área
- [ ] Habilitar/Deshabilitar
- [ ] Ver métricas de atención

### Reportes
- [ ] Turnos por día/semana/mes
- [ ] Tiempos promedio de espera
- [ ] Tiempos promedio de atención
- [ ] Turnos por categoría
- [ ] Productividad por operador
- [ ] Exportar a Excel/PDF

### Configuración
- [ ] Horarios de atención
- [ ] Mensajes del monitor
- [ ] Personalización visual
- [ ] Notificaciones
