# apps/core/models.py
# Modelos mapeados a tablas SQL Server (managed = False)
from django.db import models


# -----------------------------------------------
# 0. Usuario (tabla propia, NO usa Django Auth)
# -----------------------------------------------
class Usuario(models.Model):
    id           = models.AutoField(primary_key=True, db_column="IdUsuario")
    username     = models.CharField(max_length=150, unique=True, db_column="Username")
    display_name = models.CharField(max_length=200, db_column="DisplayName")
    email        = models.CharField(max_length=254, null=True, blank=True, db_column="Email")
    is_active    = models.BooleanField(default=True, db_column="IsActive")

    class Meta:
        managed  = False
        db_table = "Usuario"

    def __str__(self):
        return self.display_name or self.username

    @property
    def nombre_completo(self):
        return self.display_name


# -----------------------------------------------
# 0.1 Rol
# -----------------------------------------------
class Rol(models.Model):
    id          = models.SmallIntegerField(primary_key=True, db_column="IdRol")
    nombre_rol  = models.CharField(max_length=50, unique=True, db_column="NombreRol")
    descripcion = models.CharField(max_length=255, null=True, blank=True, db_column="Descripcion")

    class Meta:
        managed  = False
        db_table = "Rol"

    def __str__(self):
        return self.nombre_rol


# -----------------------------------------------
# 0.2 UsuarioRol (tabla pivote - PK compuesta)
# -----------------------------------------------
class UsuarioRol(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE,
        db_column="FkIdUsuario", primary_key=True, related_name="roles",
    )
    rol = models.ForeignKey(
        Rol, on_delete=models.CASCADE,
        db_column="FkIdRol", related_name="usuarios",
    )

    class Meta:
        managed  = False
        db_table = "UsuarioRol"
        unique_together = ("usuario", "rol")

    def __str__(self):
        return f"{self.usuario} - {self.rol}"


# -----------------------------------------------
# 1. Area / Oficina
# -----------------------------------------------
class Area(models.Model):
    id     = models.AutoField(primary_key=True, db_column="IdArea")
    nombre = models.CharField(max_length=100, unique=True, db_column="Nombre")
    slug   = models.CharField(max_length=50, unique=True, db_column="Slug")
    activa = models.BooleanField(default=True, db_column="Activa")

    class Meta:
        managed  = False
        db_table = "Area"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# -----------------------------------------------
# 1.1 AreaAdministrador
# -----------------------------------------------
class AreaAdministrador(models.Model):
    id      = models.AutoField(primary_key=True, db_column="IdAreaAdministrador")
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        db_column="FkIdUsuario", related_name="areas_administradas",
    )
    area = models.ForeignKey(
        Area, on_delete=models.CASCADE,
        db_column="FkIdArea", related_name="administradores",
    )

    class Meta:
        managed  = False
        db_table = "AreaAdministrador"
        unique_together = ("usuario", "area")

    def __str__(self):
        return f"{self.usuario} -> {self.area}"


# -----------------------------------------------
# 1.2 AreaUsuario
# -----------------------------------------------
class AreaUsuario(models.Model):
    id      = models.AutoField(primary_key=True, db_column="IdAreaUsuario")
    area = models.ForeignKey(
        Area, on_delete=models.CASCADE,
        db_column="FkIdArea", related_name="usuarios_asignados",
    )
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        db_column="FkIdUsuario", related_name="areas_asignadas",
    )

    class Meta:
        managed  = False
        db_table = "AreaUsuario"
        unique_together = ("area", "usuario")

    def __str__(self):
        return f"{self.usuario} @ {self.area}"


# -----------------------------------------------
# 2. Persona
# -----------------------------------------------
class Persona(models.Model):
    id               = models.AutoField(primary_key=True, db_column="IdPersona")
    dni              = models.IntegerField(unique=True, db_column="Dni")
    nombre           = models.CharField(max_length=120, db_column="Nombre")
    apellido         = models.CharField(max_length=120, db_column="Apellido")
    fecha_nacimiento = models.DateField(null=True, blank=True, db_column="FechaNacimiento")

    class Meta:
        managed  = False
        db_table = "Persona"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.dni})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


# -----------------------------------------------
# 3. Mesa
# -----------------------------------------------
class Mesa(models.Model):
    id     = models.AutoField(primary_key=True, db_column="IdMesa")
    area   = models.ForeignKey(
        Area, on_delete=models.DO_NOTHING,
        db_column="FkIdArea", related_name="mesas",
    )
    nombre            = models.CharField(max_length=20, db_column="Nombre")
    activa            = models.BooleanField(default=True, db_column="Activa")
    operador_asignado = models.ForeignKey(
        'Usuario', on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column="FkIdOperadorAsignado", related_name="mesas_asignadas",
    )
    color = models.CharField(max_length=7, default="#FFFFFF", db_column="Color")
    
    # Relación many-to-many con Tramite (a través de MesaTramite)
    tramites = models.ManyToManyField(
        'Tramite',
        through='MesaTramite',
        related_name='mesas_habilitadas',
        blank=True
    )

    class Meta:
        managed  = False
        db_table = "Mesa"
        ordering = ["area", "nombre"]
        unique_together = ("area", "nombre")

    def __str__(self):
        return f"{self.area} - {self.nombre}"
    
    def puede_atender_tramite(self, tramite):
        """
        Verifica si la mesa puede atender un trámite específico.
        Si no tiene trámites asignados, puede atender todos.
        """
        if not self.tramites.exists():
            return True  # Sin restricción = atiende todos
        return self.tramites.filter(id=tramite.id).exists()


# -----------------------------------------------
# 4. Tramite (ex Categoria)
# -----------------------------------------------
class Tramite(models.Model):
    id     = models.AutoField(primary_key=True, db_column="IdTramite")
    area   = models.ForeignKey(
        Area, on_delete=models.DO_NOTHING,
        db_column="FkIdArea", related_name="tramites",
    )
    nombre = models.CharField(max_length=100, db_column="Nombre")
    activa = models.BooleanField(default=True, db_column="Activa")

    class Meta:
        managed  = False
        db_table = "Tramite"
        ordering = ["nombre"]
        unique_together = ("area", "nombre")

    def __str__(self):
        return f"{self.nombre} ({self.area})"


# -----------------------------------------------
# 4.0 MesaTramite (relación many-to-many)
# -----------------------------------------------
class MesaTramite(models.Model):
    id      = models.AutoField(primary_key=True, db_column="IdMesaTramite")
    mesa    = models.ForeignKey(
        Mesa, on_delete=models.CASCADE,
        db_column="FkIdMesa", related_name="mesa_tramites"
    )
    tramite = models.ForeignKey(
        Tramite, on_delete=models.CASCADE,
        db_column="FkIdTramite", related_name="tramite_mesas"
    )

    class Meta:
        managed  = False
        db_table = "MesaTramite"
        unique_together = ("mesa", "tramite")

    def __str__(self):
        return f"{self.mesa} → {self.tramite}"


# -----------------------------------------------
# 4.1 TramiteOperador
# -----------------------------------------------
class TramiteOperador(models.Model):
    id                 = models.AutoField(primary_key=True, db_column="IdTramiteOperador")
    operador           = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        db_column="FkIdOperador", related_name="tramites_habilitados",
    )
    tramite            = models.ForeignKey(
        Tramite, on_delete=models.CASCADE,
        db_column="FkIdTramite", related_name="operadores",
    )
    habilitada         = models.BooleanField(default=True, db_column="Habilitada")
    prioridad_atencion = models.SmallIntegerField(default=1, db_column="PrioridadAtencion")

    class Meta:
        managed  = False
        db_table = "TramiteOperador"
        unique_together = ("operador", "tramite")

    def __str__(self):
        return f"{self.operador} -> {self.tramite}"


# -----------------------------------------------
# 5. EstadoTicket (catalogo)
# -----------------------------------------------
class EstadoTicket(models.Model):
    id          = models.SmallIntegerField(primary_key=True, db_column="IdEstadoTicket")
    nombre      = models.CharField(max_length=20, unique=True, db_column="Nombre")
    descripcion = models.CharField(max_length=255, db_column="Descripcion")

    class Meta:
        managed  = False
        db_table = "EstadoTicket"

    def __str__(self):
        return self.nombre


# -----------------------------------------------
# 5.1 EstadoTurno (catalogo)
# -----------------------------------------------
class EstadoTurno(models.Model):
    id          = models.SmallIntegerField(primary_key=True, db_column="IdEstadoTurno")
    nombre      = models.CharField(max_length=20, unique=True, db_column="Nombre")
    descripcion = models.CharField(max_length=255, db_column="Descripcion")

    class Meta:
        managed  = False
        db_table = "EstadoTurno"

    def __str__(self):
        return self.nombre


# -----------------------------------------------
# 6. Ticket (contenedor de turnos)
# -----------------------------------------------
class Ticket(models.Model):
    id      = models.AutoField(primary_key=True, db_column="IdTicket")
    persona = models.ForeignKey(
        Persona, on_delete=models.CASCADE,
        db_column="FkIdPersona", related_name="tickets",
    )
    area = models.ForeignKey(
        Area, on_delete=models.CASCADE,
        db_column="FkIdArea", related_name="tickets",
    )
    prioridad           = models.IntegerField(default=0, db_column="Prioridad")
    fecha_creacion      = models.DateField(db_column="FechaCreacion")
    fecha_hora_creacion = models.DateTimeField(db_column="FechaHoraCreacion")
    estado = models.ForeignKey(
        EstadoTicket, on_delete=models.DO_NOTHING,
        db_column="FkIdEstadoTicket", related_name="tickets",
    )

    # Constantes de estado (mapean a IdEstadoTicket)
    PENDIENTE  = 0
    EN_PROCESO = 1
    COMPLETADO = 2
    CANCELADO  = 3

    class Meta:
        managed  = False
        db_table = "Ticket"
        ordering = ["-fecha_hora_creacion"]

    def __str__(self):
        return f"Ticket #{self.pk} - {self.persona} ({self.area})"


# -----------------------------------------------
# 7. Turno
# -----------------------------------------------
class Turno(models.Model):
    id      = models.AutoField(primary_key=True, db_column="IdTurno")
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        db_column="FkIdTicket", related_name="turnos",
    )
    tramite = models.ForeignKey(
        Tramite, on_delete=models.DO_NOTHING,
        db_column="FkIdTramite", related_name="turnos",
    )
    orden           = models.IntegerField(default=1, db_column="Orden")
    area            = models.ForeignKey(
        Area, on_delete=models.DO_NOTHING,
        db_column="FkIdArea", related_name="turnos",
    )
    numero_visible  = models.IntegerField(default=0, db_column="NumeroVisible")
    mesa_asignada   = models.ForeignKey(
        Mesa, on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column="FkIdMesaAsignada", related_name="turnos",
    )
    estado = models.ForeignKey(
        EstadoTurno, on_delete=models.DO_NOTHING,
        db_column="FkIdEstadoTurno", related_name="turnos",
    )
    fecha_turno          = models.DateField(db_column="FechaTurno")
    fecha_hora_creacion  = models.DateTimeField(db_column="FechaHoraCreacion")
    operador             = models.ForeignKey(
        Usuario, on_delete=models.DO_NOTHING,
        null=True, blank=True,
        db_column="FkIdOperador", related_name="turnos_atendidos",
    )
    motivo_real                = models.CharField(max_length=2000, null=True, blank=True, db_column="MotivoReal")
    fecha_hora_inicio_atencion = models.DateTimeField(null=True, blank=True, db_column="FechaHoraInicioAtencion")
    fecha_hora_fin_atencion    = models.DateTimeField(null=True, blank=True, db_column="FechaHoraFinAtencion")

    # Constantes de estado (mapean a IdEstadoTurno)
    PENDIENTE    = 0
    LLAMANDO     = 1
    EN_ATENCION  = 2
    FINALIZADO   = 3
    NO_PRESENTO  = 4
    DERIVADO     = 5

    class Meta:
        managed  = False
        db_table = "Turno"
        ordering = ["-fecha_hora_creacion"]

    def __str__(self):
        nombre = self.ticket.persona.nombre_completo if self.ticket and self.ticket.persona else ""
        return f"Turno #{self.pk} - {nombre} ({self.tramite})"

    @property
    def display(self):
        """Texto breve para monitor y dashboards."""
        nombre = self.ticket.persona.nombre_completo if self.ticket and self.ticket.persona else f"N {self.numero_visible}"
        mesa = self.mesa_asignada.nombre if self.mesa_asignada else "-"
        return f"{nombre} | {self.tramite.nombre} | {mesa}"


# -----------------------------------------------
# 8. TurnoHistorialDerivacion
# -----------------------------------------------
class TurnoHistorialDerivacion(models.Model):
    id    = models.AutoField(primary_key=True, db_column="IdTurnoHistorialDerivacion")
    turno = models.ForeignKey(
        Turno, on_delete=models.CASCADE,
        db_column="FkIdTurno", related_name="derivaciones",
    )
    operador_origen = models.ForeignKey(
        Usuario, on_delete=models.DO_NOTHING,
        db_column="FkIdOperadorOrigen", related_name="derivaciones_origen",
    )
    operador_destino = models.ForeignKey(
        Usuario, on_delete=models.DO_NOTHING,
        db_column="FkIdOperadorDestino", related_name="derivaciones_destino",
    )
    fecha_hora_derivacion = models.DateTimeField(db_column="FechaHoraDerivacion")
    motivo                = models.CharField(max_length=500, null=True, blank=True, db_column="Motivo")

    class Meta:
        managed  = False
        db_table = "TurnoHistorialDerivacion"

    def __str__(self):
        return f"Derivacion Turno #{self.turno_id}: {self.operador_origen} -> {self.operador_destino}"


# -----------------------------------------------
# 9. ConfiguracionArea
# -----------------------------------------------
class ConfiguracionArea(models.Model):
    id          = models.AutoField(primary_key=True, db_column="IdConfiguracionArea")
    area        = models.ForeignKey(
        Area, on_delete=models.CASCADE,
        db_column="FkIdArea", related_name="configuraciones",
    )
    clave       = models.CharField(max_length=100, db_column="Clave")
    valor       = models.CharField(max_length=2000, db_column="Valor")
    descripcion = models.CharField(max_length=255, null=True, blank=True, db_column="Descripcion")

    class Meta:
        managed  = False
        db_table = "ConfiguracionArea"
        unique_together = ("area", "clave")

    def __str__(self):
        return f"{self.area} - {self.clave}"


# -----------------------------------------------
# 10. ConfiguracionAreaHistorial
# -----------------------------------------------
class ConfiguracionAreaHistorial(models.Model):
    id            = models.AutoField(primary_key=True, db_column="IdConfiguracionAreaHistorial")
    configuracion = models.ForeignKey(
        ConfiguracionArea, on_delete=models.CASCADE,
        db_column="FkIdConfiguracionArea", related_name="historial",
    )
    valor_anterior          = models.CharField(max_length=2000, null=True, blank=True, db_column="ValorAnterior")
    valor_nuevo             = models.CharField(max_length=2000, db_column="ValorNuevo")
    usuario_modifico        = models.ForeignKey(
        Usuario, on_delete=models.DO_NOTHING,
        db_column="FkIdUsuarioModifico", related_name="cambios_config",
    )
    fecha_hora_modificacion = models.DateTimeField(db_column="FechaHoraModificacion")

    class Meta:
        managed  = False
        db_table = "ConfiguracionAreaHistorial"

    def __str__(self):
        return f"{self.configuracion} modificada por {self.usuario_modifico}"


# -----------------------------------------------
# 11. SchemaVersion
# -----------------------------------------------
class SchemaVersion(models.Model):
    id               = models.AutoField(primary_key=True, db_column="IdVersion")
    version          = models.CharField(max_length=20, db_column="Version")
    descripcion      = models.CharField(max_length=255, db_column="Descripcion")
    fecha_aplicacion = models.DateTimeField(db_column="FechaAplicacion")

    class Meta:
        managed  = False
        db_table = "SchemaVersion"

    def __str__(self):
        return f"v{self.version} - {self.descripcion}"
