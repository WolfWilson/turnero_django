from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Tramite, Turno, Area, ConfiguracionArea, LlamadaTurno
from apps.core import services
from .forms import SolicitudTurnoForm
from .services import crear_turno


# ---------- PANTALLA DEL TÓTEM PÚBLICO ----------
def turnero_public(request):
    if request.method == "POST":
        form = SolicitudTurnoForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data["dni"] or None
            tramite = form.cleaned_data["tramite"]
            turno, _ = crear_turno(dni, tramite)
            return redirect("turnos:confirmacion", pk=turno.pk)
    else:
        form = SolicitudTurnoForm()

    tramites = Tramite.objects.filter(activa=True)
    return render(
        request,
        "turnos/turnero_public.html",
        {"form": form, "tramites": tramites},
    )


# ---------- PANTALLA DE CONFIRMACIÓN ----------
def confirmacion(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    return render(request, "turnos/confirmacion.html", {"turno": turno})


# ---------- MONITOR EN SALA DE ESPERA ----------
def monitor(request):
    hoy = timezone.localdate()
    
    # Obtener área (por query param o la primera activa)
    area_id = request.GET.get('area')
    if area_id:
        area = Area.objects.filter(pk=area_id, activa=True).first()
    else:
        area = Area.objects.filter(activa=True).first()
    
    # Obtener configuración del área
    config = services.obtener_config_area(area) if area else {}
    datos_llamada = services.obtener_datos_llamada(area) if area else {}
    
    # Turnos llamando (para mostrar en pantalla con alerta)
    turnos_llamando = Turno.objects.filter(
        fecha_turno=hoy,
        estado_id=Turno.LLAMANDO,
        **({"area": area} if area else {}),
    ).select_related(
        'ticket__persona', 'tramite', 'mesa_asignada'
    ).order_by('-fecha_hora_creacion')[:4]
    
    # Turnos en atención
    turnos_atencion = Turno.objects.filter(
        fecha_turno=hoy,
        estado_id=Turno.EN_ATENCION,
        **({"area": area} if area else {}),
    ).select_related(
        'ticket__persona', 'tramite', 'mesa_asignada'
    ).order_by('-fecha_hora_inicio_atencion')[:8]
    
    # Turnos pendientes (en espera)
    turnos_pendientes = Turno.objects.filter(
        fecha_turno=hoy,
        estado_id=Turno.PENDIENTE,
        **({"area": area} if area else {}),
    ).select_related(
        'ticket__persona', 'tramite'
    ).order_by('fecha_hora_creacion')[:20]
    
    # Todos los turnos del día para la lista
    lista = Turno.objects.filter(
        fecha_turno=hoy,
        **({"area": area} if area else {}),
    ).select_related(
        'ticket__persona', 'tramite', 'mesa_asignada', 'estado'
    ).order_by("fecha_hora_creacion")
    
    # Llamadas recientes (últimos 30 segundos) para detección en tiempo real
    # Incluye tanto LLAMADA como RELLAMADA
    tiempo_ventana = timezone.now() - timedelta(seconds=30)
    llamadas_recientes = LlamadaTurno.objects.filter(
        fecha_hora__gte=tiempo_ventana,
        turno__estado_id=Turno.LLAMANDO,
        **({"turno__area": area} if area else {}),
    ).select_related(
        'turno__ticket__persona', 'turno__tramite', 'turno__mesa_asignada'
    ).order_by('-fecha_hora')
    
    context = {
        'turnos': lista,
        'turnos_llamando': turnos_llamando,
        'turnos_atencion': turnos_atencion,
        'turnos_pendientes': turnos_pendientes,
        'llamadas_recientes': llamadas_recientes,
        'area': area,
        'config': config,
        'datos_llamada': datos_llamada,
    }
    
    return render(request, "turnos/monitor.html", context)


# ---------- TRÁMITES EN FORMATO JSON ----------
def tramites_json(request):
    data = [
        {"id": t.id, "nombre": t.nombre}
        for t in Tramite.objects.filter(activa=True).order_by("nombre")[:8]
    ]
    return JsonResponse(data, safe=False)


# ---------- API: CONFIGURACIÓN DE ÁREA ----------
def api_config_area(request, area_id=None):
    """Devuelve la configuración del área como JSON para el frontend."""
    if area_id:
        area = Area.objects.filter(pk=area_id, activa=True).first()
    else:
        area = Area.objects.filter(activa=True).first()
    
    if not area:
        return JsonResponse({'error': 'Área no encontrada'}, status=404)
    
    config = services.obtener_config_area(area)
    return JsonResponse(config)
