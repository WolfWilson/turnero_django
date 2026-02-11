from django.contrib import admin
from django.utils import timezone

from .models import (
    Usuario,
    Rol,
    UsuarioRol,
    Area,
    AreaAdministrador,
    AreaUsuario,
    Persona,
    Mesa,
    MesaTramite,
    Tramite,
    TramiteOperador,
    EstadoTicket,
    EstadoTurno,
    Ticket,
    Turno,
    ConfiguracionArea,
    ConfiguracionAreaHistorial,
    MotivoCierre,
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


class MesaTramiteInline(admin.TabularInline):
    model = MesaTramite
    extra = 1
    verbose_name = "Trámite habilitado"
    verbose_name_plural = "Trámites habilitados en esta mesa (máx 3, vacío = todos)"


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
    list_display  = ("nombre", "area", "operador_asignado", "color_preview", "activa")
    list_filter   = ("area", "activa", "operador_asignado")
    list_editable = ("activa",)
    search_fields = ("nombre",)
    fields        = ("area", "nombre", "operador_asignado", "color", "activa")
    inlines       = [MesaTramiteInline]
    
    def color_preview(self, obj):
        return f'<span style="display:inline-block;width:20px;height:20px;background:{obj.color};border:1px solid #ccc;"></span> {obj.color}'
    color_preview.short_description = "Color"
    color_preview.allow_tags = True


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
#   ConfiguracionArea (fieldsets)
# ───────────────────────────────
class ConfigHistorialInline(admin.TabularInline):
    model = ConfiguracionAreaHistorial
    extra = 0
    readonly_fields = ("campo_modificado", "valor_anterior", "valor_nuevo",
                       "usuario_modifico", "fecha_hora_modificacion")
    can_delete = False
    max_num = 0  # solo lectura
    verbose_name = "Cambio registrado"
    verbose_name_plural = "Historial de cambios"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ConfiguracionArea)
class ConfiguracionAreaAdmin(admin.ModelAdmin):
    list_display = ("area", "resumen_turnos", "resumen_horario", "mensaje_pantalla")
    list_filter  = ("area",)
    inlines      = [ConfigHistorialInline]

    fieldsets = (
        ("Área", {
            "fields": ("area",),
        }),
        ("🎫 Turnos", {
            "fields": (
                "permitir_sin_dni",
                "multiples_turnos_dni",
                "max_turnos_por_dia",
                "vencimiento_turnos",
            ),
            "description": "Reglas para la emisión y gestión de turnos.",
        }),
        ("⭐ Prioridades", {
            "fields": (
                "prioridad_adulto_mayor",
                "prioridad_embarazadas",
                "prioridad_discapacidad",
            ),
            "description": "Las prioridades habilitadas estarán disponibles solo para operadores logueados, no en el tótem público.",
        }),
        ("🖥️ Visuales", {
            "fields": (
                "mensaje_pantalla",
                "media_habilitada",
            ),
            "description": "Personalización visual del monitor y pantallas.",
        }),
        ("⚙️ Operación", {
            "fields": (
                "permitir_derivaciones",
                "requiere_motivo_fin",
            ),
            "description": "Comportamiento de los operadores durante la atención.",
        }),
        ("🕐 Horarios de Atención", {
            "fields": (
                ("emision_hora_inicio", "emision_hora_fin"),
                ("atencion_hora_inicio", "atencion_hora_fin"),
            ),
            "description": "Emisión: franja horaria en la que el tótem público permite sacar turnos. Atención: horario informativo / corte de llamados.",
        }),
        ("🔔 Configuración General", {
            "fields": (
                "tiempo_llamada_seg",
                "voz_llamada",
                "sonido_llamada",
            ),
            "description": "Alertas y notificaciones al llamar turnos.",
        }),
    )

    def resumen_turnos(self, obj):
        sin_dni = "✅" if obj.permitir_sin_dni else "❌"
        multi = "✅" if obj.multiples_turnos_dni else "❌"
        return f"Sin DNI: {sin_dni} | Múltiples: {multi} | Máx: {obj.max_turnos_por_dia}/día"
    resumen_turnos.short_description = "Turnos"

    def resumen_horario(self, obj):
        ei = obj.emision_hora_inicio.strftime("%H:%M") if obj.emision_hora_inicio else "-"
        ef = obj.emision_hora_fin.strftime("%H:%M") if obj.emision_hora_fin else "-"
        return f"{ei} – {ef}"
    resumen_horario.short_description = "Emisión"

    def save_model(self, request, obj, form, change):
        """Registra en auditoría cada campo que cambió."""
        if change:
            try:
                old = ConfiguracionArea.objects.get(pk=obj.pk)
                # Buscar el usuario del sistema (mapeo Django User → Usuario)
                from .models import Usuario
                try:
                    usuario = Usuario.objects.get(username=request.user.username)
                except Usuario.DoesNotExist:
                    usuario = Usuario.objects.first()  # fallback

                ahora = timezone.now()
                for field in form.changed_data:
                    valor_ant = str(getattr(old, field, ''))
                    valor_new = str(getattr(obj, field, ''))
                    ConfiguracionAreaHistorial.objects.create(
                        configuracion=obj,
                        campo_modificado=field,
                        valor_anterior=valor_ant,
                        valor_nuevo=valor_new,
                        usuario_modifico=usuario,
                        fecha_hora_modificacion=ahora,
                    )
            except ConfiguracionArea.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)


# ───────────────────────────────
#   MotivoCierre Admin
# ───────────────────────────────
@admin.register(MotivoCierre)
class MotivoCierreAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'orden', 'descripcion')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo', 'orden')
    ordering = ('orden', 'nombre')
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'activo', 'orden')
        }),
    )
