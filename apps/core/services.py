from datetime import date
import json
from pathlib import Path

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from .models import Area, Tramite, Mesa, Persona, Ticket, Turno, EstadoTicket, EstadoTurno

# --- "SP" ficticio ---
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


# --- Servicio central ---
@transaction.atomic
def emitir_turno(area: Area, tramite: Tramite, dni: int | None) -> Turno:
    """
    Crea un Ticket + Turno segun el nuevo esquema.
    Devuelve el Turno (nuevo o existente si la persona ya tiene uno pendiente).
    """
    ahora = timezone.now()
    hoy   = ahora.date()

    # 1) Persona
    persona = None
    if dni:
        datos = buscar_persona_por_dni(dni)
        if not datos:
            raise ValueError("DNI no encontrado en padron")
        persona, _ = Persona.objects.get_or_create(
            dni=dni,
            defaults=dict(nombre=datos["nombre"], apellido=datos["apellido"]),
        )

        # Ya tiene un turno pendiente o llamando en esta area?
        existente = Turno.objects.filter(
            ticket__persona=persona,
            area=area,
            estado_id__in=[Turno.PENDIENTE, Turno.LLAMANDO],
        ).first()
        if existente:
            return existente

    if persona is None:
        raise ValueError("Se requiere DNI para emitir turno")

    # 2) Numeracion visible del dia
    ultimo = (
        Turno.objects.filter(area=area, fecha_turno=hoy)
        .aggregate(Max("numero_visible"))["numero_visible__max"] or 0
    )
    numero_visible = ultimo + 1

    # 3) Crear Ticket (contenedor)
    estado_ticket_pend = EstadoTicket.objects.get(pk=Ticket.PENDIENTE)
    ticket = Ticket.objects.create(
        persona=persona,
        area=area,
        prioridad=0,
        fecha_creacion=hoy,
        fecha_hora_creacion=ahora,
        estado=estado_ticket_pend,
    )

    # 4) Crear Turno
    estado_turno_pend = EstadoTurno.objects.get(pk=Turno.PENDIENTE)
    turno = Turno.objects.create(
        ticket=ticket,
        tramite=tramite,
        orden=1,
        area=area,
        numero_visible=numero_visible,
        estado=estado_turno_pend,
        fecha_turno=hoy,
        fecha_hora_creacion=ahora,
    )

    return turno
