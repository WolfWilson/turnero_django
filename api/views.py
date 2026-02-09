from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.core import services
from apps.core.models import Tramite, Turno
from .serializers import TurnoEmitirSerializer, BuscarPersonaSerializer


class BuscarPersona(APIView):
    """
    POST  /api/personas/buscar/   {"dni": 12345678}
    200 → {"dni": 12345678, "nombre": "MARÍA", "apellido": "SÁNCHEZ"}
    404 → {"detail": "..."}
    """
    def post(self, request):
        ser = BuscarPersonaSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dni = ser.validated_data["dni"]

        datos = services.buscar_persona_por_dni(dni)
        if not datos:
            return Response({"detail": "DNI no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        return Response(datos)


class EmitirTurno(APIView):
    """
    POST  /api/turnos/emitir/
    """
    def post(self, request):
        ser = TurnoEmitirSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        tramite = Tramite.objects.select_related("area").get(
            pk=ser.validated_data["tramite_id"]
        )
        dni = ser.validated_data.get("dni")

        try:
            turno = services.emitir_turno(tramite.area, tramite, dni)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        espera = Turno.objects.filter(
            area=tramite.area,
            estado_id=Turno.PENDIENTE,
            fecha_hora_creacion__lt=turno.fecha_hora_creacion,
        ).count()

        nombre_visible = (
            turno.ticket.persona.nombre_completo
            if turno.ticket and turno.ticket.persona
            else f"N° {turno.numero_visible}"
        )

        return Response({
            "turno_id":  turno.id,
            "nombre":    nombre_visible,
            "tramite":   tramite.nombre,
            "espera":    espera,
        })
