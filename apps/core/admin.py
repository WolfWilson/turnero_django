from django.contrib import admin

from .models import (
    Area,
    AreaAdministrador,
    Categoria,
    CategoriaOperador,
    Mesa,
    Persona,
    Turno,
    Atencion,
)

# ───────────────────────────────
#   Inlines útiles
# ───────────────────────────────
class CategoriaOperadorInline(admin.TabularInline):
    model = CategoriaOperador
    extra = 1


# ───────────────────────────────
#   Área
# ───────────────────────────────
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "activa")
    list_editable = ("activa",)
    prepopulated_fields = {"slug": ("nombre",)}
    search_fields = ("nombre", "slug")


# ───────────────────────────────
#   Administradores de Área
# ───────────────────────────────
@admin.register(AreaAdministrador)
class AreaAdministradorAdmin(admin.ModelAdmin):
    list_display = ("usuario", "area")
    list_filter  = ("area",)
    autocomplete_fields = ("usuario", "area")


# ───────────────────────────────
#   Categoría
# ───────────────────────────────
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "area", "activa")
    list_filter   = ("area", "activa")
    list_editable = ("activa",)
    search_fields = ("nombre",)
    inlines       = [CategoriaOperadorInline]


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
#   Turno
# ───────────────────────────────
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display   = ("display", "estado", "creado_en")
    list_filter    = ("area", "estado", "fecha")
    autocomplete_fields = ("categoria", "mesa_asignada", "persona")

    #necesario para el searchfields
    search_fields = ("numero", "", "persona__dni", "persona__apellido", "persona__nombre", "categoria__nombre")


# ───────────────────────────────
#   Atención
# ───────────────────────────────
@admin.register(Atencion)
class AtencionAdmin(admin.ModelAdmin):
    list_display   = ("turno", "operador", "iniciado_en", "finalizado_en")
    list_filter    = ("operador", "iniciado_en", "finalizado_en")
    autocomplete_fields = ("turno", "operador")
