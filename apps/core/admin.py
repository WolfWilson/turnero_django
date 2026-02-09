from django.contrib import admin

from .models import (
    Usuario,
    Rol,
    UsuarioRol,
    Area,
    AreaAdministrador,
    AreaUsuario,
    Persona,
    Mesa,
    Tramite,
    TramiteOperador,
    EstadoTicket,
    EstadoTurno,
    Ticket,
    Turno,
    ConfiguracionArea,
)


# ───────────────────────────────
#   Inlines
# ───────────────────────────────
class UsuarioRolInline(admin.TabularInline):
    model = UsuarioRol
    extra = 1


class TramiteOperadorInline(admin.TabularInline):
    model = TramiteOperador
    extra = 1


# ───────────────────────────────
#   Usuario
# ───────────────────────────────
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display  = ("username", "display_name", "is_active")
    list_editable = ("is_active",)
    search_fields = ("username", "display_name")
    inlines       = [UsuarioRolInline]


# ───────────────────────────────
#   Rol
# ───────────────────────────────
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display  = ("nombre_rol", "descripcion")
    search_fields = ("nombre_rol",)


# ───────────────────────────────
#   Área
# ───────────────────────────────
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "activa")
    list_editable = ("activa",)
    search_fields = ("nombre", "slug")


# ───────────────────────────────
#   Administradores de Área
# ───────────────────────────────
@admin.register(AreaAdministrador)
class AreaAdministradorAdmin(admin.ModelAdmin):
    list_display = ("usuario", "area")
    list_filter  = ("area",)


# ───────────────────────────────
#   AreaUsuario
# ───────────────────────────────
@admin.register(AreaUsuario)
class AreaUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "area")
    list_filter  = ("area",)


# ───────────────────────────────
#   Tramite (ex Categoría)
# ───────────────────────────────
@admin.register(Tramite)
class TramiteAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "area", "activa")
    list_filter   = ("area", "activa")
    list_editable = ("activa",)
    search_fields = ("nombre",)
    inlines       = [TramiteOperadorInline]


# ───────────────────────────────
#   Mesa
# ───────────────────────────────
@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "area", "activa")
    list_filter   = ("area", "activa")
    list_editable = ("activa",)
    search_fields = ("nombre",)


# ───────────────────────────────
#   Persona
# ───────────────────────────────
@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display  = ("dni", "apellido", "nombre")
    search_fields = ("dni", "apellido", "nombre")


# ───────────────────────────────
#   Catálogos de estado
# ───────────────────────────────
@admin.register(EstadoTicket)
class EstadoTicketAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion")


@admin.register(EstadoTurno)
class EstadoTurnoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion")


# ───────────────────────────────
#   Ticket
# ───────────────────────────────
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display  = ("id", "persona", "area", "estado", "fecha_hora_creacion")
    list_filter   = ("area", "estado")
    search_fields = ("persona__dni", "persona__apellido")


# ───────────────────────────────
#   Turno
# ───────────────────────────────
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display  = ("id", "numero_visible", "tramite", "area", "estado", "fecha_hora_creacion")
    list_filter   = ("area", "estado", "fecha_turno")
    search_fields = ("numero_visible", "ticket__persona__dni")


# ───────────────────────────────
#   ConfiguracionArea
# ───────────────────────────────
@admin.register(ConfiguracionArea)
class ConfiguracionAreaAdmin(admin.ModelAdmin):
    list_display = ("area", "clave", "valor")
    list_filter  = ("area",)
