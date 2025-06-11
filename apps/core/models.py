from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# ----------------------------------------------------------------------
# 1. Entidades de configuración
# ----------------------------------------------------------------------
class Categoria(models.Model):
    """Tipo de trámite que el público elige (Certificaciones, Reclamos…)."""
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Mesa(models.Model):
    """Puesto físico de atención."""
    nombre = models.CharField(
        max_length=20,
        unique=True,
        help_text="Identificador visible (Mesa 1, Mesa 2, etc.)",
    )
    activa = models.BooleanField(default=True)
    categorias = models.ManyToManyField(
        Categoria,
        blank=True,
        help_text="Si la lista está vacía, la mesa acepta cualquier categoría.",
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


# ----------------------------------------------------------------------
# 2. Datos de la persona (solo para Modo 2)
# ----------------------------------------------------------------------
class Persona(models.Model):
    """Ciudadano que se identifica con DNI."""
    dni = models.PositiveBigIntegerField(unique=True)
    nombre = models.CharField(max_length=120)
    apellido = models.CharField(max_length=120)

    class Meta:
        verbose_name = "persona"
        verbose_name_plural = "personas"
        ordering = ["apellido", "nombre"]

    def __str__(self) -> str:
        return f"{self.apellido}, {self.nombre} ({self.dni})"

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"


# ----------------------------------------------------------------------
# 3. Turno (compatible con ambos modos)
# ----------------------------------------------------------------------
class Turno(models.Model):
    """Turno emitido desde la pantalla pública."""

    class Modo(models.TextChoices):
        NUMERACION = "ticket", "Ticket numerado"
        DNI = "dni", "Identificación por DNI"

    class Estado(models.TextChoices):
        PENDIENTE = "pend", "Pendiente"
        EN_ATENCION = "prog", "En atención"
        FINALIZADO = "done", "Finalizado"

    # --- Campos generales ------------------------------------------------
    modo = models.CharField(
        max_length=6,
        choices=Modo.choices,
        default=Modo.NUMERACION,
        help_text="Define si el turno usa numeración o DNI.",
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    mesa_asignada = models.ForeignKey(
        Mesa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Se completará al asignar la mesa.",
    )
    estado = models.CharField(
        max_length=4,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    fecha = models.DateField(auto_now_add=True, editable=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    # --- Campos para Modo 1 (ticket) ------------------------------------
    numero = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Número secuencial (solo para modo Ticket).",
    )

    # --- Campos para Modo 2 (DNI) ---------------------------------------
    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Persona identificada (solo para modo DNI).",
    )

    class Meta:
        ordering = ["-creado_en"]
        constraints = [
            # Un número único por día (modo Ticket)
            models.UniqueConstraint(
                fields=["numero", "fecha"],
                condition=models.Q(modo="ticket"),
                name="uniq_numero_por_fecha",
            ),
            # Un turno activo por persona (modo DNI)
            models.UniqueConstraint(
                fields=["persona"],
                condition=models.Q(
                    modo="dni",
                    estado__in=["pend", "prog"],
                ),
                name="uniq_turno_activo_por_persona",
            ),
        ]

    # ------------------ Métodos útiles ----------------------------------
    def __str__(self) -> str:
        if self.modo == self.Modo.NUMERACION:
            return f"T-{self.numero:04d} ({self.categoria.nombre})"
        return f"{self.persona} – {self.categoria.nombre}"

    @property
    def display(self) -> str:
        """Texto breve para pantallas públicas."""
        if self.modo == self.Modo.NUMERACION:
            return (
                f"N° {self.numero} • {self.categoria.nombre} "
                f"• Mesa {self.mesa_asignada}"
            )
        nombre = self.persona.nombre_completo if self.persona else ""
        return (
            f"{nombre} • {self.categoria.nombre} "
            f"• Mesa {self.mesa_asignada}"
        )


# ----------------------------------------------------------------------
# 4. Registro de la atención
# ----------------------------------------------------------------------
class Atencion(models.Model):
    """Se crea cuando el operador hace “play” e inicia la atención."""
    turno = models.OneToOneField(Turno, on_delete=models.CASCADE)
    operador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={"groups__name": "Operador"},
    )
    motivo_real = models.TextField(verbose_name="detalle / motivo final")
    iniciado_en = models.DateTimeField(auto_now_add=True)
    finalizado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-iniciado_en"]

    def __str__(self) -> str:
        return f"Atención #{self.turno.pk} por {self.operador}"
