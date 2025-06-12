from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def postlogin(request):
    """Redirige al panel correcto según el grupo del usuario."""
    if request.user.groups.filter(name="Director").exists():
        return redirect("administracion:home")   # dashboard admin
    if request.user.groups.filter(name="Operador").exists():
        return redirect("atencion:panel_mesa")   # panel operador
    return redirect("logout")    # sin grupo válido → fuerza logout
