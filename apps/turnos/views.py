from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from apps.core.models import Tramite, Turno
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
    lista = Turno.objects.filter(fecha_turno=hoy).order_by("fecha_hora_creacion")
    return render(request, "turnos/monitor.html", {"turnos": lista})


# ---------- TRÁMITES EN FORMATO JSON ----------
def tramites_json(request):
    data = [
        {"id": t.id, "nombre": t.nombre}
        for t in Tramite.objects.filter(activa=True).order_by("nombre")[:8]
    ]
    return JsonResponse(data, safe=False)
