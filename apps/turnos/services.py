from django.db import connection, transaction, models
from django.utils import timezone
from apps.core.models import (
    Turno,
    Mesa,
    Categoria,
    Persona,
    Turno as T,
)

# ----------------------------------------------------------------------
# Utilidades internas
# ----------------------------------------------------------------------
def _siguiente_numero() -> int:
    today = timezone.localdate()
    ultimo = (
        Turno.objects.filter(fecha=today, modo="ticket")
        .aggregate(models.Max("numero"))["numero__max"]
        or 0
    )
    return ultimo + 1


def _asignar_mesa(categoria: Categoria) -> Mesa | None:
    """Devuelve la primera mesa activa compatible con la categoría."""
    compatibles = (
        Mesa.objects.filter(activa=True)
        .filter(
            models.Q(categorias=categoria) | models.Q(categorias__isnull=True)
        )
        .distinct()
    )
    return compatibles.first()


# ----------------------------------------------------------------------
# API principal
# ----------------------------------------------------------------------
def crear_turno(dni: str | None, categoria: Categoria):
    """
    Crea un turno:
    - Modo DNI si el parámetro `dni` tiene valor.
    - Modo Ticket si `dni` es None o cadena vacía.
    Devuelve (turno, creado_bool).
    """
    with transaction.atomic():
        if dni:
            # ---------------- MODO 2 (DNI) ----------------
            persona, _ = Persona.objects.get_or_create(dni=dni)
            # Aquí podrías invocar el SP y completar nombre/apellido
            turno_existente = Turno.objects.filter(
                persona=persona,
                estado__in=["pend", "prog"],
            ).first()
            if turno_existente:
                return turno_existente, False

            mesa = _asignar_mesa(categoria)
            turno = Turno.objects.create(
                modo="dni",
                categoria=categoria,
                persona=persona,
                mesa_asignada=mesa,
            )
            return turno, True

        # ---------------- MODO 1 (TICKET) ----------------
        numero = _siguiente_numero()
        mesa = _asignar_mesa(categoria)
        turno = Turno.objects.create(
            modo="ticket",
            numero=numero,
            categoria=categoria,
            mesa_asignada=mesa,
        )
        return turno, True
