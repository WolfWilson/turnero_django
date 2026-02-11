from datetime import date, datetime, time, timedelta
from django.db import transaction
from django.db.models import Max, Count
from django.utils import timezone
import logging

from .models import (
    Area, Tramite, Mesa, Persona, Ticket, Turno,
    EstadoTicket, EstadoTurno, ConfiguracionArea,
    TurnoHistorialDerivacion, Usuario,
)
from .services_aportes import buscar_persona_por_dni as buscar_en_aportes

logger = logging.getLogger(__name__)


# =====================================================================
#  BÚSQUEDA DE PERSONA
# =====================================================================
def buscar_persona_por_dni(dni: int) -> dict | None:
    """
    Busca persona en base de datos Aportes (SQL Server sql01).
    
    Returns:
        dict con keys: 'nombre', 'apellido', 'fecha_nacimiento' (opcional), 'sexo' (opcional)
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
    
    # Formatear fecha si existe
    fecha_nac_str = None
    fecha_nac_obj = None
    if resultado.get('fecha_nac'):
        try:
            fecha_obj = resultado['fecha_nac']
            if hasattr(fecha_obj, 'strftime'):
                fecha_nac_str = fecha_obj.strftime('%d/%m/%Y')
                fecha_nac_obj = fecha_obj if isinstance(fecha_obj, date) else fecha_obj.date() if hasattr(fecha_obj, 'date') else None
            else:
                fecha_nac_str = str(fecha_obj)
        except Exception:
            fecha_nac_str = None
    
    return {
        'nombre': partes[1].strip() if len(partes) > 1 else '',
        'apellido': partes[0].strip() if partes else apeynom,
        'fecha_nacimiento': fecha_nac_str,
        'fecha_nacimiento_date': fecha_nac_obj,  # Para cálculo de edad
        'sexo': resultado.get('sexo'),
    }


# =====================================================================
#  CÁLCULO DE PRIORIDAD AUTOMÁTICA
# =====================================================================
def calcular_prioridad(config: ConfiguracionArea, persona_data: dict | None) -> int:
    """
    Calcula la prioridad automática del turno según configuración del área.
    
    Prioridades:
        0 = Normal (sin prioridad)
        1 = Prioridad baja (adulto mayor)
        2 = Prioridad media (embarazada — requiere selección manual)
        3 = Prioridad alta (discapacidad — requiere selección manual)
    
    Auto-detección:
        - Adulto mayor: se detecta automáticamente por fecha de nacimiento (≥65 años)
        - Embarazadas y discapacidad: se pasan como flags explícitos en persona_data
    
    Returns:
        int: nivel de prioridad (mayor = más prioritario)
    """
    if not persona_data:
        return 0
    
    prioridad = 0
    
    # ── Adulto mayor: auto-detección por edad ──
    if config.prioridad_adulto_mayor:
        fecha_nac = persona_data.get('fecha_nacimiento_date')
        if fecha_nac and isinstance(fecha_nac, date):
            hoy = date.today()
            edad = hoy.year - fecha_nac.year - (
                (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day)
            )
            if edad >= 65:
                prioridad = max(prioridad, 1)
                logger.info(f"Prioridad adulto mayor aplicada (edad: {edad})")
    
    # ── Embarazada: flag explícito ──
    if config.prioridad_embarazadas and persona_data.get('es_embarazada'):
        prioridad = max(prioridad, 2)
        logger.info("Prioridad embarazada aplicada")
    
    # ── Discapacidad: flag explícito ──
    if config.prioridad_discapacidad and persona_data.get('es_discapacitado'):
        prioridad = max(prioridad, 3)
        logger.info("Prioridad discapacidad aplicada")
    
    return prioridad


# =====================================================================
#  EMISIÓN DE TURNO
# =====================================================================
@transaction.atomic
def emitir_turno(
    area: Area,
    tramite: Tramite,
    dni: int | None,
    prioridad: int = 0,
    es_embarazada: bool = False,
    es_discapacitado: bool = False,
) -> Turno:
    """
    Crea un Ticket + Turno según el esquema.
    Respeta ConfiguracionArea para validaciones y prioridades.
    Devuelve el Turno (nuevo o existente si la persona ya tiene uno pendiente).
    """
    ahora = timezone.now()
    ahora_local = timezone.localtime(ahora)
    hoy   = ahora_local.date()
    config = ConfiguracionArea.get_for_area(area)

    # ── Validar horario de emisión (hora local Argentina) ──
    hora_actual = ahora_local.time()
    if config.emision_hora_inicio and config.emision_hora_fin:
        if hora_actual < config.emision_hora_inicio or hora_actual > config.emision_hora_fin:
            inicio = config.emision_hora_inicio.strftime("%H:%M")
            fin = config.emision_hora_fin.strftime("%H:%M")
            raise ValueError(
                f"Fuera del horario de emisión de turnos ({inicio} a {fin}). "
                f"Intente nuevamente dentro del horario establecido."
            )

    # ── Vencer turnos del día anterior ──
    if config.vencimiento_turnos:
        _vencer_turnos_anteriores(area, hoy)

    # ── Validar DNI ──
    persona = None
    persona_data = None
    if dni:
        persona_data = buscar_persona_por_dni(dni)
        if not persona_data:
            raise ValueError("DNI no encontrado en padrón")
        
        # Inyectar flags de prioridad manual
        persona_data['es_embarazada'] = es_embarazada
        persona_data['es_discapacitado'] = es_discapacitado
        
        persona, _ = Persona.objects.get_or_create(
            dni=dni,
            defaults=dict(nombre=persona_data["nombre"], apellido=persona_data["apellido"]),
        )

        # ── Ya tiene un turno pendiente o llamando? ──
        if not config.multiples_turnos_dni:
            existente = Turno.objects.filter(
                ticket__persona=persona,
                area=area,
                estado_id__in=[Turno.PENDIENTE, Turno.LLAMANDO],
            ).first()
            if existente:
                return existente

        # ── Validar máximo de turnos por día ──
        turnos_hoy = Turno.objects.filter(
            ticket__persona=persona,
            area=area,
            fecha_turno=hoy,
        ).count()
        if turnos_hoy >= config.max_turnos_por_dia:
            raise ValueError(
                f"Ha alcanzado el límite de {config.max_turnos_por_dia} turno(s) por día."
            )
    elif not config.permitir_sin_dni:
        raise ValueError("Se requiere DNI para emitir turno")

    if persona is None and not config.permitir_sin_dni:
        raise ValueError("Se requiere DNI para emitir turno")

    # ── Calcular prioridad automática ──
    prioridad_calculada = calcular_prioridad(config, persona_data)
    prioridad_final = max(prioridad, prioridad_calculada)

    # ── Numeración visible del día ──
    ultimo = (
        Turno.objects.filter(area=area, fecha_turno=hoy)
        .aggregate(Max("numero_visible"))["numero_visible__max"] or 0
    )
    numero_visible = ultimo + 1

    # ── Crear Ticket (contenedor) ──
    estado_ticket_pend = EstadoTicket.objects.get(pk=Ticket.PENDIENTE)
    ticket = Ticket.objects.create(
        persona=persona,
        area=area,
        prioridad=prioridad_final,
        fecha_creacion=hoy,
        fecha_hora_creacion=ahora,
        estado=estado_ticket_pend,
    )

    # ── Crear Turno ──
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


# =====================================================================
#  OPERACIONES DEL OPERADOR
# =====================================================================
@transaction.atomic
def llamar_turno(turno: Turno, operador: Usuario, mesa: Mesa) -> Turno:
    """
    El operador llama al siguiente turno.
    Cambia estado de PENDIENTE → LLAMANDO y asigna mesa/operador.
    Respeta ConfiguracionArea.atencion_hora_inicio/fin.
    """
    config = ConfiguracionArea.get_for_area(turno.area)
    
    # ── Validar horario de atención ──
    _validar_horario_atencion(config)
    
    if turno.estado_id != Turno.PENDIENTE:
        raise ValueError(f"El turno no está en estado pendiente (estado actual: {turno.estado.nombre})")
    
    estado_llamando = EstadoTurno.objects.get(pk=Turno.LLAMANDO)
    turno.estado = estado_llamando
    turno.operador = operador
    turno.mesa_asignada = mesa
    turno.save()
    
    # Actualizar ticket a EN_PROCESO
    estado_ticket_proceso = EstadoTicket.objects.get(pk=Ticket.EN_PROCESO)
    turno.ticket.estado = estado_ticket_proceso
    turno.ticket.save()
    
    logger.info(f"Turno #{turno.id} llamado por {operador} en {mesa}")
    return turno


@transaction.atomic
def iniciar_atencion(turno: Turno) -> Turno:
    """
    Pasa turno de LLAMANDO → EN_ATENCION.
    Registra la hora de inicio de atención.
    """
    if turno.estado_id != Turno.LLAMANDO:
        raise ValueError(f"El turno debe estar en estado LLAMANDO (actual: {turno.estado.nombre})")
    
    estado_atencion = EstadoTurno.objects.get(pk=Turno.EN_ATENCION)
    turno.estado = estado_atencion
    turno.fecha_hora_inicio_atencion = timezone.now()
    turno.save()
    
    logger.info(f"Turno #{turno.id} - atención iniciada")
    return turno


@transaction.atomic
def finalizar_atencion(turno: Turno, motivo: str | None = None) -> Turno:
    """
    Pasa turno de EN_ATENCION → FINALIZADO.
    Respeta ConfiguracionArea.requiere_motivo_fin.
    """
    config = ConfiguracionArea.get_for_area(turno.area)
    
    if turno.estado_id != Turno.EN_ATENCION:
        raise ValueError(f"El turno debe estar EN_ATENCION (actual: {turno.estado.nombre})")
    
    # ── Validar motivo si es requerido ──
    if config.requiere_motivo_fin and not motivo:
        raise ValueError("Se requiere un motivo para finalizar el turno")
    
    estado_finalizado = EstadoTurno.objects.get(pk=Turno.FINALIZADO)
    turno.estado = estado_finalizado
    turno.motivo_real = motivo
    turno.fecha_hora_fin_atencion = timezone.now()
    turno.save()
    
    # Cerrar ticket
    estado_ticket_completado = EstadoTicket.objects.get(pk=Ticket.COMPLETADO)
    turno.ticket.estado = estado_ticket_completado
    turno.ticket.save()
    
    logger.info(f"Turno #{turno.id} finalizado. Motivo: {motivo or 'N/A'}")
    return turno


@transaction.atomic
def marcar_no_presento(turno: Turno) -> Turno:
    """Marca turno como NO_PRESENTO (la persona no acudió al llamado)."""
    if turno.estado_id not in [Turno.LLAMANDO, Turno.PENDIENTE]:
        raise ValueError(f"No se puede marcar como ausente (estado: {turno.estado.nombre})")
    
    estado_no_presento = EstadoTurno.objects.get(pk=Turno.NO_PRESENTO)
    turno.estado = estado_no_presento
    turno.save()
    
    logger.info(f"Turno #{turno.id} - no se presentó")
    return turno


@transaction.atomic
def derivar_turno(
    turno: Turno,
    operador_origen: Usuario,
    operador_destino: Usuario,
    motivo: str | None = None,
) -> Turno:
    """
    Deriva un turno a otro operador.
    Solo disponible si ConfiguracionArea.permitir_derivaciones es True.
    """
    config = ConfiguracionArea.get_for_area(turno.area)
    
    if not config.permitir_derivaciones:
        raise ValueError("Las derivaciones no están habilitadas para esta área")
    
    if turno.estado_id not in [Turno.LLAMANDO, Turno.EN_ATENCION]:
        raise ValueError(f"No se puede derivar en estado {turno.estado.nombre}")
    
    # Registrar historial de derivación
    TurnoHistorialDerivacion.objects.create(
        turno=turno,
        operador_origen=operador_origen,
        operador_destino=operador_destino,
        fecha_hora_derivacion=timezone.now(),
        motivo=motivo,
    )
    
    # Cambiar estado a DERIVADO y luego volver a PENDIENTE para el nuevo operador
    estado_pendiente = EstadoTurno.objects.get(pk=Turno.PENDIENTE)
    turno.estado = estado_pendiente
    turno.operador = None  # Se reasigna al ser llamado por el destino
    turno.mesa_asignada = None
    turno.save()
    
    logger.info(f"Turno #{turno.id} derivado de {operador_origen} a {operador_destino}")
    return turno


def obtener_proximo_turno(area: Area) -> Turno | None:
    """
    Obtiene el siguiente turno a atender, respetando prioridad y orden de llegada.
    Turnos con mayor prioridad se atienden primero.
    A igual prioridad, se atiende por orden de creación (FIFO).
    Incluye turnos pendientes de días anteriores que no fueron vencidos.
    """
    return (
        Turno.objects.filter(
            area=area,
            estado_id=Turno.PENDIENTE,
        )
        .select_related('ticket__persona', 'tramite')
        .order_by('-ticket__prioridad', 'fecha_hora_creacion')
        .first()
    )


# =====================================================================
#  CONFIGURACIÓN PARA FRONTEND
# =====================================================================
def obtener_config_area(area: Area) -> dict:
    """
    Retorna la configuración completa del área como dict para el frontend.
    Usada por API y vistas para inyectar parámetros en templates/JS.
    """
    config = ConfiguracionArea.get_for_area(area)
    return {
        # Turnos
        'permitir_sin_dni': config.permitir_sin_dni,
        'multiples_turnos_dni': config.multiples_turnos_dni,
        'max_turnos_por_dia': config.max_turnos_por_dia,
        'vencimiento_turnos': config.vencimiento_turnos,
        # Prioridades
        'prioridad_adulto_mayor': config.prioridad_adulto_mayor,
        'prioridad_embarazadas': config.prioridad_embarazadas,
        'prioridad_discapacidad': config.prioridad_discapacidad,
        # Visuales
        'mensaje_pantalla': config.mensaje_pantalla,
        'media_habilitada': config.media_habilitada,
        # Operación
        'permitir_derivaciones': config.permitir_derivaciones,
        'requiere_motivo_fin': config.requiere_motivo_fin,
        # Horarios
        'emision_hora_inicio': config.emision_hora_inicio.strftime('%H:%M') if config.emision_hora_inicio else None,
        'emision_hora_fin': config.emision_hora_fin.strftime('%H:%M') if config.emision_hora_fin else None,
        'atencion_hora_inicio': config.atencion_hora_inicio.strftime('%H:%M') if config.atencion_hora_inicio else None,
        'atencion_hora_fin': config.atencion_hora_fin.strftime('%H:%M') if config.atencion_hora_fin else None,
        # General
        'tiempo_llamada_seg': config.tiempo_llamada_seg,
        'voz_llamada': config.voz_llamada,
        'sonido_llamada': config.sonido_llamada,
    }


# =====================================================================
#  UTILIDADES INTERNAS
# =====================================================================
def _vencer_turnos_anteriores(area: Area, hoy: date) -> int:
    """
    Marca como NO_PRESENTO los turnos pendientes de días anteriores.
    Retorna la cantidad de turnos vencidos.
    """
    estado_no_presento = EstadoTurno.objects.get(pk=Turno.NO_PRESENTO)
    vencidos = Turno.objects.filter(
        area=area,
        fecha_turno__lt=hoy,
        estado_id__in=[Turno.PENDIENTE, Turno.LLAMANDO],
    ).update(estado=estado_no_presento)
    return vencidos


def _validar_horario_atencion(config: ConfiguracionArea) -> None:
    """
    Valida que estamos dentro del horario de atención (hora local Argentina).
    Lanza ValueError si estamos fuera de horario.
    """
    hora_actual = timezone.localtime().time()
    if config.atencion_hora_inicio and config.atencion_hora_fin:
        if hora_actual < config.atencion_hora_inicio or hora_actual > config.atencion_hora_fin:
            inicio = config.atencion_hora_inicio.strftime("%H:%M")
            fin = config.atencion_hora_fin.strftime("%H:%M")
            raise ValueError(
                f"Fuera del horario de atención ({inicio} a {fin}). "
                f"No se pueden realizar acciones fuera de este horario."
            )


def esta_en_horario_emision(area: Area) -> dict:
    """
    Verifica si el tótem puede emitir turnos en este momento (hora local Argentina).
    Retorna dict con 'permitido' (bool) y 'mensaje' (str).
    """
    config = ConfiguracionArea.get_for_area(area)
    hora_actual = timezone.localtime().time()

    if config.emision_hora_inicio and config.emision_hora_fin:
        if hora_actual < config.emision_hora_inicio or hora_actual > config.emision_hora_fin:
            inicio = config.emision_hora_inicio.strftime("%H:%M")
            fin = config.emision_hora_fin.strftime("%H:%M")
            return {
                'permitido': False,
                'mensaje': f"El horario de emisión de turnos es de {inicio} a {fin} hs."
            }

    return {'permitido': True, 'mensaje': ''}


def esta_en_horario_atencion(area: Area) -> dict:
    """
    Verifica si se puede atender turnos en este momento (hora local Argentina).
    Retorna dict con 'permitido' (bool) y 'mensaje' (str).
    """
    config = ConfiguracionArea.get_for_area(area)
    hora_actual = timezone.localtime().time()

    if config.atencion_hora_inicio and config.atencion_hora_fin:
        if hora_actual < config.atencion_hora_inicio or hora_actual > config.atencion_hora_fin:
            inicio = config.atencion_hora_inicio.strftime("%H:%M")
            fin = config.atencion_hora_fin.strftime("%H:%M")
            return {
                'permitido': False,
                'mensaje': f"El horario de atención es de {inicio} a {fin} hs."
            }

    return {'permitido': True, 'mensaje': ''}


def obtener_datos_llamada(area: Area) -> dict:
    """
    Retorna la configuración de llamada para el monitor/frontend.
    Incluye tiempo de alerta, y flags de voz/sonido.
    """
    config = ConfiguracionArea.get_for_area(area)
    return {
        'tiempo_llamada_seg': config.tiempo_llamada_seg,
        'voz_llamada': config.voz_llamada,
        'sonido_llamada': config.sonido_llamada,
    }
