from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

def es_operador(u):
    return u.groups.filter(name="Operador").exists()

@login_required
@user_passes_test(es_operador)
def panel_mesa(request):
    return render(request, "operador/panel.html")
