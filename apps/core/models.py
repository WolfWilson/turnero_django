from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# ---------------------------------------------------------------------
# 0. Área / Oficina
# ---------------------------------------------------------------------
class Area(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug   = models.SlugField(unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "área"
        verbose_name_plural = "áreas"

    def __str__(self):
        return self.nombre


# ---------------------------------------------------------------------
# 0.1  Administradores de área (rol granular)
# ---------------------------------------------------------------------
class AreaAdministrador(models.Model):
    """Vincula un usuario con privilegios de administración a un área."""
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,               # al borrar el usuario, cae la vinculación
        related_name="areas_administradas",
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,               # si el área se elimina, se limpian vínculos
        related_name="administradores",
    )

    class Meta:
        unique_together = ("usuario", "area")
        verbose_name = "administrador de área"
        verbose_name_plural = "administradores de área"

    def __str__(self):
        return f"{self.usuario} ↔ {self.area}"


# ---------------------------------------------------------------------
# 1. Categorías y Mesas
# ---------------------------------------------------------------------
class Categoria(models.Model):
    area   = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,               # impedir borrar un área con categorías
        related_name="categorias",
    )
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ["nombre"]
        unique_together = ("area", "nombre")
        verbose_name = "categoría"

    def __str__(self):
        return f"{self.nombre} ({self.area})"


class Mesa(models.Model):
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,               # no borrar área con mesas activas
        related_name="mesas",
    )
    nombre = models.CharField(max_length=20)
    activa = models.BooleanField(default=True)
    categorias = models.ManyToManyField(
        Categoria,
        blank=True,
        related_name="mesas",
        help_text="Si está vacío, la mesa atiende cualquier categoría.",
    )

    class Meta:
        ordering = ["area", "nombre"]
        unique_together = ("area", "nombre")
        verbose_name = "mesa"

    def __str__(self):
        return f"{self.area} · {self.nombre}"


# ---------------------------------------------------------------------
# 2. Persona (modo DNI)
# ---------------------------------------------------------------------
class Persona(models.Model):
    dni      = models.PositiveBigIntegerField(unique=True)
    nombre   = models.CharField(max_length=120)
    apellido = models.CharField(max_length=120)

    class Meta:
        ordering = ["apellido", "nombre"]
        verbose_name = "persona"

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.dni})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


# ---------------------------------------------------------------------
# 3. Turno
# ---------------------------------------------------------------------
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
        on_delete=models.SET_NULL,    # si se desactiva una mesa, mantenemos el histórico
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
# --- en Turno.display -----------------------------------
    def display(self) -> str:
        if self.modo == self.Modo.NUMERACION:
            return f"N° {self.numero} • {self.categoria} • Mesa {self.mesa_asignada}"
        nombre = self.persona.nombre_completo if self.persona else ""  # ← seguro
        return f"{nombre} • {self.categoria} • Mesa {self.mesa_asignada}"


# ---------------------------------------------------------------------
# 4. Atención
# ---------------------------------------------------------------------
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

    def __str__(self):
        return f"{self.turno.area} · Atención #{self.turno.pk} por {self.operador}"
