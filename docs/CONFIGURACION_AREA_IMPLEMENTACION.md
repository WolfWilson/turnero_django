# ConfiguracionArea — Implementación Completa

> **Fecha:** 2026-02-11  
> **Versión del schema:** 1.3.0  
> **Estado:** ✅ Todos los 17 campos integrados como parámetros de comportamiento

---

## Resumen

La tabla `ConfiguracionArea` almacena 17 campos estructurados que controlan el comportamiento
del sistema turnero por área. Cada campo ahora **actúa como parámetro de comportamiento real**
en la lógica del backend y/o frontend.

---

## Tabla de Campos e Implementación

### 🎫 TURNOS (4 campos)

| Campo | Tipo | Dónde se usa | Comportamiento |
|-------|------|-------------|----------------|
| `PermitirSinDni` | BIT | `services.emitir_turno()` | Si es `False`, rechaza turnos sin DNI con error |
| `MultiplesTurnosDni` | BIT | `services.emitir_turno()` | Si es `False`, retorna turno existente en vez de crear uno nuevo |
| `MaxTurnosPorDia` | SMALLINT | `services.emitir_turno()` | Limita cantidad de turnos por persona por día |
| `VencimientoTurnos` | BIT | `services.emitir_turno()` | Si es `True`, marca como NO_PRESENTO turnos de días anteriores |

### ⭐ PRIORIDADES (3 campos)

| Campo | Tipo | Dónde se usa | Comportamiento |
|-------|------|-------------|----------------|
| `PrioridadAdultoMayor` | BIT | `services.calcular_prioridad()` | **Auto-detecta** personas ≥65 años por fecha de nacimiento del padrón. Asigna prioridad=1 |
| `PrioridadEmbarazadas` | BIT | `services.calcular_prioridad()` | Acepta flag `es_embarazada` del frontend. Asigna prioridad=2 |
| `PrioridadDiscapacidad` | BIT | `services.calcular_prioridad()` | Acepta flag `es_discapacitado` del frontend. Asigna prioridad=3 |

**Cómo funciona la prioridad:**
- `obtener_proximo_turno()` ordena por `-ticket__prioridad` (mayor primero) y luego por FIFO
- El panel del operador muestra badge ⭐ en turnos prioritarios y los resalta en la tabla
- La API `/api/turnos/emitir/` acepta `es_embarazada` y `es_discapacitado` como parámetros opcionales

### 🖥️ VISUALES (2 campos)

| Campo | Tipo | Dónde se usa | Comportamiento |
|-------|------|-------------|----------------|
| `MensajePantalla` | NVARCHAR(150) | `monitor.html` | Se muestra como texto configurable al pie de la lista de turnos en el monitor |
| `MediaHabilitada` | BIT | `monitor.html` | Controla si se renderiza la sección de video/media. Si es `False`, no se muestra el `<video>` |

### ⚙️ OPERACIÓN (2 campos)

| Campo | Tipo | Dónde se usa | Comportamiento |
|-------|------|-------------|----------------|
| `PermitirDerivaciones` | BIT | `services.derivar_turno()` + `panel.html` | Si es `False`, el botón "Derivar" no aparece en el panel y el service lanza error |
| `RequiereMotivoFin` | BIT | `services.finalizar_atencion()` + `panel.html` | Si es `True`, el service rechaza finalización sin motivo. El modal lo indica como requerido |

### 🕐 HORARIOS (4 campos)

| Campo | Tipo | Dónde se usa | Comportamiento |
|-------|------|-------------|----------------|
| `EmisionHoraInicio` | TIME | `services.emitir_turno()` | Valida que la hora actual esté dentro del rango permitido para emitir turnos |
| `EmisionHoraFin` | TIME | `services.emitir_turno()` | Rechaza emisión fuera de horario con mensaje detallado |
| `AtencionHoraInicio` | TIME | `services.llamar_turno()` + `panel.html` | Valida que el operador pueda llamar turnos dentro del horario. Panel muestra mensaje si fuera de horario |
| `AtencionHoraFin` | TIME | `services.llamar_turno()` + `panel.html` | Bloquea acciones del operador fuera de horario |

### 🔔 GENERAL (3 campos)

| Campo | Tipo | Dónde se usa | Comportamiento |
|-------|------|-------------|----------------|
| `TiempoLlamadaSeg` | SMALLINT | `monitor.html` → JS | Define la duración del overlay de alerta en el monitor (en segundos). Default: 10s |
| `VozLlamada` | BIT | `monitor.html` → JS | **Placeholder funcional**: Usa Web Speech API (`speechSynthesis`) para anunciar el turno por TTS. Dice: "Turno de [nombre], dirigirse a [mesa]" |
| `SonidoLlamada` | BIT | `monitor.html` → JS | Controla si se reproduce un sonido al llamar turno. Elemento `<audio>` presente. TODO: agregar archivo .mp3 real |

---

## Archivos Modificados

### Backend

| Archivo | Cambios |
|---------|---------|
| `apps/core/services.py` | Reescrito completo: `calcular_prioridad()`, operaciones del operador (`llamar_turno`, `iniciar_atencion`, `finalizar_atencion`, `derivar_turno`, `marcar_no_presento`, `obtener_proximo_turno`), `obtener_config_area()`, `_validar_horario_atencion()`, `esta_en_horario_atencion()`, `obtener_datos_llamada()` |
| `apps/atencion/views.py` | 7 nuevos endpoints API: `api_llamar_turno`, `api_iniciar_atencion`, `api_finalizar_atencion`, `api_no_presento`, `api_proximo_turno`, `api_derivar_turno`. Panel ahora inyecta config JSON |
| `apps/atencion/urls.py` | 6 nuevas rutas API bajo `/atencion/api/` |
| `apps/turnos/views.py` | Monitor refactorizado con queries separadas (llamando/atención), config inyectada. Nuevo endpoint `api_config_area` |
| `apps/turnos/urls.py` | 2 nuevas rutas para config API |
| `api/views.py` | `BuscarPersona` filtra `fecha_nacimiento_date`, `EmitirTurno` acepta prioridades, nuevo `ConfiguracionAreaAPI` |
| `api/serializers.py` | `TurnoEmitirSerializer` acepta `es_embarazada` y `es_discapacitado` |
| `api/urls.py` | 2 nuevas rutas config |

### Frontend

| Archivo | Cambios |
|---------|---------|
| `templates/operador/panel.html` | JS funcional completo: `apiFetch()`, `iniciarAtencion()`, `finalizarAtencion()` con modal de motivo, `noPresento()`, `proximoTurno()`, `derivarTurno()`, `seleccionarTurno()`. Toast de notificaciones. Badge de prioridad. Columna prioridad en tabla |
| `templates/turnos/monitor.html` | `MONITOR_CONFIG` inyectado en JS. Duración alerta configurable. TTS con Web Speech API (voz_llamada). Sonido con `<audio>`. Mensaje configurable. Media condicional. Separación de turnos llamando/atención |

---

## API Endpoints

### Endpoints del Operador (`/atencion/api/`)

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/atencion/api/llamar/<turno_id>/` | Llamar un turno específico |
| POST | `/atencion/api/iniciar/<turno_id>/` | Iniciar atención |
| POST | `/atencion/api/finalizar/<turno_id>/` | Finalizar atención (body: `{motivo}`) |
| POST | `/atencion/api/no-presento/<turno_id>/` | Marcar como no presentado |
| POST | `/atencion/api/proximo/` | Obtener y llamar siguiente turno |
| POST | `/atencion/api/derivar/<turno_id>/` | Derivar turno (body: `{operador_destino_id, motivo}`) |

### Endpoints de Configuración

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/config/` | Config del área por defecto |
| GET | `/api/config/<area_id>/` | Config de un área específica |
| GET | `/turnos/api/config/` | Alias público |

---

## Notas de Implementación

### Voz de Llamada (Placeholder Funcional)
- Usa la **Web Speech API** nativa del navegador (`window.speechSynthesis`)
- No requiere archivos de audio ni servicios externos
- Anuncia: *"Turno de [nombre], dirigirse a [mesa]"* en español argentino
- Se activa solo si `VozLlamada = 1` en la configuración del área
- Funciona en Chrome, Edge, Firefox modernos

### Sonido de Llamada (Placeholder)
- Elemento `<audio>` presente en el DOM con `id="alert-sound"`
- El archivo de sonido (`sonido_llamada.mp3`) debe colocarse en `static/media/`
- Se reproduce al mostrar la alerta si `SonidoLlamada = 1`
- El `play()` tiene catch para manejar restricciones de autoplay

### Prioridad de Adulto Mayor
- **Auto-detectada** sin intervención del usuario
- Calcula la edad a partir de `fecha_nacimiento` del padrón Aportes
- Umbral: ≥ 65 años
- No requiere flag manual — se aplica automáticamente al emitir turno

### Cola de Prioridad
- `obtener_proximo_turno()` ordena: mayor prioridad primero, luego FIFO
- Niveles: 0=Normal, 1=Adulto Mayor, 2=Embarazada, 3=Discapacidad
- El operador ve badge ⭐ en turnos prioritarios
