from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from apps.core.models import Categoria, Turno
from .forms import SolicitudTurnoForm
from .services import crear_turno


# ---------- PANTALLA DEL TÓTEM PÚBLICO ----------
def turnero_public(request):
    if request.method == "POST":
        form = SolicitudTurnoForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data["dni"] or None
            categoria = form.cleaned_data["categoria"]
            turno, _ = crear_turno(dni, categoria)
            return redirect("turnos:confirmacion", pk=turno.pk)
    else:
        form = SolicitudTurnoForm()

    categorias = Categoria.objects.all()
    return render(
        request,
        "turnos/turnero_public.html",
        {"form": form, "categorias": categorias},
    )


# ---------- PANTALLA DE CONFIRMACIÓN ----------
def confirmacion(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    return render(request, "turnos/confirmacion.html", {"turno": turno})


# ---------- MONITOR EN SALA DE ESPERA ----------
def monitor(request):
    hoy = timezone.localdate()
    lista = Turno.objects.filter(fecha=hoy).order_by("creado_en")
    return render(request, "turnos/monitor.html", {"turnos": lista})
