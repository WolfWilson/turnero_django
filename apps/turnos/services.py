from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from apps.core.models import (
    Turno,
    Ticket,
    Tramite,
    Persona,
    EstadoTicket,
    EstadoTurno,
)


# ----------------------------------------------------------------------
# API principal
# ----------------------------------------------------------------------
def crear_turno(dni: str | None, tramite: Tramite):
    """
    Crea Ticket + Turno.
    - Requiere DNI.
    - Si ya existe turno pendiente/llamando, devuelve el existente.
    Devuelve (turno, creado_bool).
    """
    ahora = timezone.now()
    hoy   = ahora.date()

    with transaction.atomic():
        if not dni:
            raise ValueError("Se requiere DNI para emitir turno")

        persona, _ = Persona.objects.get_or_create(dni=int(dni))

        # Turno existente pendiente?
        turno_existente = Turno.objects.filter(
            ticket__persona=persona,
            area=tramite.area,
            estado_id__in=[Turno.PENDIENTE, Turno.LLAMANDO],
        ).first()
        if turno_existente:
            return turno_existente, False

        # Numeracion
        ultimo = (
            Turno.objects.filter(area=tramite.area, fecha_turno=hoy)
            .aggregate(Max("numero_visible"))["numero_visible__max"] or 0
        )
        numero_visible = ultimo + 1

        # Ticket
        estado_ticket_pend = EstadoTicket.objects.get(pk=Ticket.PENDIENTE)
        ticket = Ticket.objects.create(
            persona=persona,
            area=tramite.area,
            prioridad=0,
            fecha_creacion=hoy,
            fecha_hora_creacion=ahora,
            estado=estado_ticket_pend,
        )

        # Turno
        estado_turno_pend = EstadoTurno.objects.get(pk=Turno.PENDIENTE)
        turno = Turno.objects.create(
            ticket=ticket,
            tramite=tramite,
            orden=1,
            area=tramite.area,
            numero_visible=numero_visible,
            estado=estado_turno_pend,
            fecha_turno=hoy,
            fecha_hora_creacion=ahora,
        )
        return turno, True
