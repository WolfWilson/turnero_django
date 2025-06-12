from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils import timezone            # ← faltaba
from apps.core.models import Turno


def es_director(user):
    return user.groups.filter(name="Director").exists()


@login_required
@user_passes_test(es_director)
def dashboard_admin(request):
    """Resumen general para el director."""
    hoy = timezone.localdate()
    stats = {
        "pendientes":   Turno.objects.filter(estado="pend").count(),
        "en_atencion":  Turno.objects.filter(estado="prog").count(),
        "finalizados":  Turno.objects.filter(estado="done", fecha=hoy).count(),
    }
    return render(
        request,
        "admin/dashboard_admin.html",
        {"stats": stats},
    )
