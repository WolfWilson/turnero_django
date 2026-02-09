# 📊 Modelos de Datos

## Diagrama de Entidades

```
┌──────────────────┐
│      User        │ (Django Auth)
└────────┬─────────┘
         │
         │ 1:N
         ▼
┌──────────────────┐      ┌──────────────────┐
│AreaAdministrador │◄────►│      Area        │
└──────────────────┘      └────────┬─────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
     │  Categoria   │     │    Mesa      │     │    Turno     │
     └──────┬───────┘     └──────────────┘     └──────┬───────┘
            │                                         │
            │ M:N                                     │ 1:1
            ▼                                         ▼
   ┌──────────────────┐                      ┌──────────────┐
   │CategoriaOperador │                      │   Atencion   │
   └──────────────────┘                      └──────────────┘
                                                     │
                                                     ▼
                                             ┌──────────────┐
                                             │   Persona    │
                                             └──────────────┘
```

## Detalle de Modelos

### Area

Representa una oficina o sector de atención.

```python
class Area(models.Model):
    nombre = CharField(max_length=100, unique=True)
    slug   = SlugField(unique=True)
    activa = BooleanField(default=True)
```

| Campo   | Tipo        | Descripción                        |
|---------|-------------|------------------------------------|
| nombre  | CharField   | Nombre del área (único)            |
| slug    | SlugField   | Identificador URL-friendly         |
| activa  | BooleanField| Permite deshabilitar sin eliminar  |

---

### AreaAdministrador

Vincula usuarios con privilegios de administración a un área.

```python
class AreaAdministrador(models.Model):
    usuario = ForeignKey(User)
    area    = ForeignKey(Area)
```

| Campo   | Tipo       | Descripción                    |
|---------|------------|--------------------------------|
| usuario | ForeignKey | Usuario administrador          |
| area    | ForeignKey | Área que administra            |

**Constraint**: `unique_together = ("usuario", "area")`

---

### Categoria

Tipo de trámite o consulta dentro de un área.

```python
class Categoria(models.Model):
    area       = ForeignKey(Area)
    nombre     = CharField(max_length=100)
    activa     = BooleanField(default=True)
    operadores = ManyToManyField(User, through="CategoriaOperador")
```

| Campo      | Tipo          | Descripción                      |
|------------|---------------|----------------------------------|
| area       | ForeignKey    | Área a la que pertenece          |
| nombre     | CharField     | Nombre de la categoría           |
| activa     | BooleanField  | Visible para emisión/atención    |
| operadores | ManyToManyField| Operadores habilitados          |

---

### CategoriaOperador

Relación operador-categoría con habilitación.

```python
class CategoriaOperador(models.Model):
    operador   = ForeignKey(User)
    categoria  = ForeignKey(Categoria)
    habilitada = BooleanField(default=True)
```

---

### Mesa

Puesto físico de atención.

```python
class Mesa(models.Model):
    area   = ForeignKey(Area)
    nombre = CharField(max_length=20)
    activa = BooleanField(default=True)
```

| Campo  | Tipo       | Descripción                    |
|--------|------------|--------------------------------|
| area   | ForeignKey | Área donde está la mesa        |
| nombre | CharField  | Identificador (ej: "Mesa 1")   |
| activa | BooleanField| Mesa disponible para atención |

---

### Persona

Identificación por DNI.

```python
class Persona(models.Model):
    dni      = PositiveBigIntegerField(unique=True)
    nombre   = CharField(max_length=120)
    apellido = CharField(max_length=120)
```

| Campo    | Tipo                 | Descripción              |
|----------|----------------------|--------------------------|
| dni      | PositiveBigIntegerField | Documento único       |
| nombre   | CharField            | Nombre de pila           |
| apellido | CharField            | Apellido                 |

**Propiedad**: `nombre_completo` → `"{nombre} {apellido}"`

---

### Turno

Turno emitido en el sistema.

```python
class Turno(models.Model):
    class Modo(TextChoices):
        NUMERACION = "ticket", "Ticket numerado"
        DNI        = "dni", "Identificación por DNI"

    class Estado(TextChoices):
        PENDIENTE   = "pend", "Pendiente"
        EN_ATENCION = "prog", "En atención"
        FINALIZADO  = "done", "Finalizado"

    area          = ForeignKey(Area)
    modo          = CharField(choices=Modo)
    categoria     = ForeignKey(Categoria)
    mesa_asignada = ForeignKey(Mesa, null=True)
    estado        = CharField(choices=Estado, default=PENDIENTE)
    fecha         = DateField(auto_now_add=True)
    creado_en     = DateTimeField(auto_now_add=True)
    numero        = PositiveIntegerField(null=True)  # modo ticket
    persona       = ForeignKey(Persona, null=True)   # modo DNI
```

**Constraints**:
- `uniq_numero_area_fecha`: Número único por área/fecha en modo ticket
- `uniq_turno_activo_persona_area`: Solo un turno activo por persona/área

---

### Atencion

Registro de atención de un turno.

```python
class Atencion(models.Model):
    turno         = OneToOneField(Turno)
    operador      = ForeignKey(User)
    motivo_real   = TextField()
    iniciado_en   = DateTimeField(auto_now_add=True)
    finalizado_en = DateTimeField(null=True)
```

| Campo         | Tipo          | Descripción                    |
|---------------|---------------|--------------------------------|
| turno         | OneToOneField | Turno atendido                 |
| operador      | ForeignKey    | Operador que atendió           |
| motivo_real   | TextField     | Descripción real del trámite   |
| iniciado_en   | DateTimeField | Inicio de la atención          |
| finalizado_en | DateTimeField | Fin de la atención             |
