from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from apps.core.models import Usuario, UsuarioRol


def es_operador(user):
    try:
        usuario = Usuario.objects.get(username=user.username)
        return UsuarioRol.objects.filter(
            usuario=usuario,
            rol__nombre_rol="Operador",
        ).exists()
    except Usuario.DoesNotExist:
        return False


@login_required
@user_passes_test(es_operador)
def panel_mesa(request):
    return render(request, "operador/panel.html")
