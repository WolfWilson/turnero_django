# 🔌 API REST

## Información General

La API REST está construida con **Django REST Framework** y proporciona endpoints para operaciones que requieren interacción AJAX desde el frontend.

**Base URL**: `/api/`

## Endpoints

### POST `/api/personas/buscar/`

Busca una persona en el padrón por su DNI.

#### Request

```json
{
  "dni": 12345678
}
```

#### Response 200 OK

```json
{
  "dni": 12345678,
  "nombre": "MARÍA",
  "apellido": "SÁNCHEZ"
}
```

#### Response 404 Not Found

```json
{
  "detail": "DNI no encontrado"
}
```

---

### POST `/api/turnos/emitir/`

Emite un nuevo turno para una categoría.

#### Request

```json
{
  "categoria_id": 1,
  "dni": 12345678  // opcional, si no se envía usa modo ticket
}
```

#### Response 200 OK

```json
{
  "turno_id": 42,
  "nombre": "MARÍA SÁNCHEZ",  // o "N° 15" en modo ticket
  "categoria": "Consulta General",
  "espera": 3  // turnos pendientes delante
}
```

#### Response 400 Bad Request

```json
{
  "detail": "Ya existe un turno activo para esta persona"
}
```

---

## Serializers

### TurnoEmitirSerializer

```python
class TurnoEmitirSerializer(serializers.Serializer):
    categoria_id = serializers.IntegerField(required=True)
    dni = serializers.IntegerField(required=False, allow_null=True)
```

### BuscarPersonaSerializer

```python
class BuscarPersonaSerializer(serializers.Serializer):
    dni = serializers.IntegerField(required=True)
```

---

## Lógica de Negocio

### Emisión de Turno

1. Validar datos de entrada
2. Obtener categoría y su área asociada
3. Si hay DNI:
   - Buscar persona en padrón
   - Verificar si ya tiene turno activo
   - Crear turno en modo DNI
4. Si no hay DNI:
   - Generar siguiente número del día
   - Crear turno en modo ticket
5. Asignar mesa disponible (si existe)
6. Retornar datos del turno creado

### Búsqueda de Persona

1. Consultar fixture `personas.json` (simula SP de padrón)
2. Retornar datos o 404 si no existe

---

## Ejemplos de Uso

### JavaScript (Fetch)

```javascript
// Buscar persona
const response = await fetch('/api/personas/buscar/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({ dni: 12345678 })
});

// Emitir turno
const turno = await fetch('/api/turnos/emitir/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({
    categoria_id: 1,
    dni: 12345678
  })
});
```

### Python (requests)

```python
import requests

# Buscar persona
response = requests.post(
    'http://localhost:8000/api/personas/buscar/',
    json={'dni': 12345678}
)

# Emitir turno
response = requests.post(
    'http://localhost:8000/api/turnos/emitir/',
    json={'categoria_id': 1, 'dni': 12345678}
)
```
