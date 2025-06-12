# Create your views here.
# apps/atencion/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def panel_mesa(request):
    return render(request, "base_private.html", {"message": "Panel de operador en construcción"})
