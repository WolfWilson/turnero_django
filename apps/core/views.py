from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Usuario, UsuarioRol


def _get_usuario_roles(user) -> list[str]:
    """Devuelve lista de nombres de rol del usuario Django Auth en la tabla UsuarioRol."""
    try:
        usuario = Usuario.objects.get(username=user.username)
        return list(
            UsuarioRol.objects.filter(usuario=usuario)
            .values_list("rol__nombre_rol", flat=True)
        )
    except Usuario.DoesNotExist:
        return []


@login_required
def postlogin(request):
    """Redirige al panel correcto según el rol en UsuarioRol."""
    roles = _get_usuario_roles(request.user)

    if "Director" in roles or "SuperAdmin" in roles:
        return redirect("administracion:home")
    if "Operador" in roles:
        return redirect("atencion:panel_mesa")
    # sin rol válido → fuerza logout
    logout(request)
    return redirect("login")


