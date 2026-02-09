# apps/core/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# ───────────────────────────────────────────────
# 0. Área / Oficina
# ───────────────────────────────────────────────
class Area(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug   = models.SlugField(unique=True)
    activa = models.BooleanField(
        default=True,
        help_text="Permite deshabilitar un área sin eliminarla"
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "área"
        verbose_name_plural = "áreas"

    def __str__(self):
        return self.nombre


# ───────────────────────────────────────────────
# 0.1  Administradores de área
# ───────────────────────────────────────────────
class AreaAdministrador(models.Model):
    """Vincula un usuario con privilegios de administración a un área."""
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="areas_administradas",
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name="administradores",
    )

    class Meta:
        unique_together = ("usuario", "area")
        verbose_name = "administrador de área"
        verbose_name_plural = "administradores de área"

    def __str__(self):
        return f"{self.usuario} ↔ {self.area}"


# ───────────────────────────────────────────────
# 1. Categorías de atención
# ───────────────────────────────────────────────
class Categoria(models.Model):
    area   = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name="categorias",
    )
    nombre = models.CharField(max_length=100)
    activa = models.BooleanField(
        default=True,
        help_text="Oculta o muestra la categoría para emisión y atención"
    )

    # Operadores habilitados para atenderla (through con flag)
    operadores = models.ManyToManyField(
        User,
        through="CategoriaOperador",
        related_name="categorias_habilitadas",
        blank=True,
        limit_choices_to={"groups__name": "Operador"},
    )

    class Meta:
        ordering = ["nombre"]
        unique_together = ("area", "nombre")
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        estado = "✔" if self.activa else "✖"
        return f"{self.nombre} ({self.area}) {estado}"


class CategoriaOperador(models.Model):
    """Relación operador ↔ categoría con posibilidad de habilitar/deshabilitar."""
    operador   = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria  = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    habilitada = models.BooleanField(default=True)

    class Meta:
        unique_together = ("operador", "categoria")
        verbose_name = "categoría habilitada a operador"
        verbose_name_plural = "categorías habilitadas a operadores"

    def __str__(self):
        estado = "✔" if self.habilitada else "✖"
        return f"{self.operador} → {self.categoria} {estado}"


# ───────────────────────────────────────────────
# 1.b Mesas de atención
# ───────────────────────────────────────────────
class Mesa(models.Model):
    area   = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name="mesas",
    )
    nombre = models.CharField(max_length=20)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["area", "nombre"]
        unique_together = ("area", "nombre")
        verbose_name = "mesa"
        verbose_name_plural = "mesas"

    def __str__(self):
        estado = "✔" if self.activa else "✖"
        return f"{self.area} · {self.nombre} {estado}"


# ───────────────────────────────────────────────
# 2. Persona (identificación por DNI)
# ───────────────────────────────────────────────
class Persona(models.Model):
    dni      = models.PositiveBigIntegerField(unique=True)
    nombre   = models.CharField(max_length=120)
    apellido = models.CharField(max_length=120)

    class Meta:
        ordering = ["apellido", "nombre"]
        verbose_name = "persona"
        verbose_name_plural = "personas"

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.dni})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


# ───────────────────────────────────────────────
# 3. Turno
# ───────────────────────────────────────────────
class Turno(models.Model):

    class Modo(models.TextChoices):
        NUMERACION = "ticket", "Ticket numerado"
        DNI        = "dni",    "Identificación por DNI"

    class Estado(models.TextChoices):
        PENDIENTE   = "pend", "Pendiente"
        EN_ATENCION = "prog", "En atención"
        FINALIZADO  = "done", "Finalizado"

    area      = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="turnos")
    modo      = models.CharField(max_length=6, choices=Modo.choices, default=Modo.DNI)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    mesa_asignada = models.ForeignKey(
        Mesa,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    estado    = models.CharField(max_length=4, choices=Estado.choices, default=Estado.PENDIENTE)
    fecha     = models.DateField(auto_now_add=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    # modo Ticket
    numero = models.PositiveIntegerField(null=True, blank=True)

    # modo DNI
    persona = models.ForeignKey(Persona, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        ordering = ["-creado_en"]
        constraints = [
            # número único por área y fecha para modo ticket
            models.UniqueConstraint(
                fields=["area", "numero", "fecha"],
                condition=models.Q(modo="ticket"),
                name="uniq_numero_area_fecha",
            ),
            # solo un turno activo por persona y área
            models.UniqueConstraint(
                fields=["area", "persona"],
                condition=models.Q(modo="dni", estado__in=["pend", "prog"]),
                name="uniq_turno_activo_persona_area",
            ),
        ]

    def __str__(self):
        if self.modo == self.Modo.NUMERACION:
            return f"{self.area} · T-{self.numero:04d} ({self.categoria})"
        return f"{self.area} · {self.persona} – {self.categoria}"

    @property
    def display(self) -> str:
        """Texto breve para carteles o dashboards."""
        if self.modo == self.Modo.NUMERACION:
            return f"N° {self.numero} • {self.categoria} • Mesa {self.mesa_asignada}"
        nombre = self.persona.nombre_completo if self.persona else ""
        return f"{nombre} • {self.categoria} • Mesa {self.mesa_asignada}"


# ───────────────────────────────────────────────
# 4. Atención
# ───────────────────────────────────────────────
class Atencion(models.Model):
    turno = models.OneToOneField(Turno, on_delete=models.CASCADE)
    operador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={"groups__name": "Operador"},
    )
    motivo_real   = models.TextField()
    iniciado_en   = models.DateTimeField(auto_now_add=True)
    finalizado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-iniciado_en"]
        verbose_name = "atención"
        verbose_name_plural = "atenciones"

    def __str__(self):
        return f"{self.turno.area} · Atención #{self.turno.pk} por {self.operador}"
