from datetime import date
import json
from pathlib import Path

from django.db import transaction
from django.db.models import Max, Q
from django.db.utils import IntegrityError

from .models import Area, Categoria, Mesa, Persona, Turno

# ─── “SP” ficticio ───────────────────────────────────────────────────
_JSON_PATH = Path(__file__).resolve().parent / "fixtures" / "personas.json"

try:
    with _JSON_PATH.open(encoding="utf8") as f:
        _PERSONAS_FAKE = {p["dni"]: p for p in json.load(f)}
except FileNotFoundError:
    _PERSONAS_FAKE = {}
except json.JSONDecodeError as e:
    raise RuntimeError(f"personas.json mal formado: {e}") from e


def buscar_persona_por_dni(dni: int) -> dict | None:
    return _PERSONAS_FAKE.get(dni)


# ─── Servicio central ────────────────────────────────────────────────
@transaction.atomic
def emitir_turno(area: Area, categoria: Categoria, dni: int | None) -> Turno:
    """
    Devuelve un Turno (nuevo o existente) según reglas de negocio.
    Puede lanzar ValueError con mensaje para el usuario.
    """
    hoy = date.today()

    # 1) Persona (modo DNI)
    persona = None
    if dni:
        datos = buscar_persona_por_dni(dni)
        if not datos:
            raise ValueError("DNI no encontrado en padrón")
        persona, _ = Persona.objects.get_or_create(
            dni=dni,
            defaults=dict(nombre=datos["nombre"], apellido=datos["apellido"])
        )

        # ¿Ya tiene un turno pendiente o en atención?
        existente = Turno.objects.filter(
            area=area,
            persona=persona,
            estado__in=[Turno.Estado.PENDIENTE, Turno.Estado.EN_ATENCION],
        ).first()
        if existente:
            return existente  # devolvemos el mismo turno, no se crea otro

    # 2) Mesa sugerida
    mesa = (
        Mesa.objects.filter(activa=True, area=area)
        .filter(Q(categorias=categoria) | Q(categorias=None))
        .order_by("id")
        .first()
    )

    # 3) Numeración (modo ticket)
    modo = Turno.Modo.DNI
    numero = None
    if persona is None:
        modo = Turno.Modo.NUMERACION
        ultimo = (
            Turno.objects.filter(area=area, fecha=hoy, modo=modo)
            .aggregate(Max("numero"))["numero__max"] or 0
        )
        numero = ultimo + 1

    # 4) Crear turno
    try:
        turno = Turno.objects.create(
            area=area,
            categoria=categoria,
            persona=persona,
            modo=modo,
            numero=numero,
            mesa_asignada=mesa,
        )
    except IntegrityError:
        # Si llegara a colarse (raro por la comprobación previa)
        raise ValueError("Ya existe un turno activo para esta persona")

    return turno
