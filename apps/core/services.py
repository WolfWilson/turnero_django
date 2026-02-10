from datetime import date
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from .models import Area, Tramite, Mesa, Persona, Ticket, Turno, EstadoTicket, EstadoTurno
from .services_aportes import buscar_persona_por_dni as buscar_en_aportes


def buscar_persona_por_dni(dni: int) -> dict | None:
    """
    Busca persona en base de datos Aportes (SQL Server sql01).
    
    Returns:
        dict con keys: 'nombre', 'apellido', 'fecha_nacimiento' (opcional)
        o None si no encuentra
    """
    # Convertir DNI a string de 8 dígitos
    dni_str = str(dni).zfill(8) if isinstance(dni, int) else str(dni)
    resultado = buscar_en_aportes(dni_str)
    
    if not resultado:
        return None
    
    # Convertir formato de Aportes a formato esperado
    apeynom = resultado['apeynom'].strip()
    partes = apeynom.split(',', 1)
    
    return {
        'nombre': partes[1].strip() if len(partes) > 1 else '',
        'apellido': partes[0].strip() if partes else apeynom,
        'fecha_nacimiento': resultado.get('fecha_nac'),
        'sexo': resultado.get('sexo'),
    }


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
