from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.core import services
from apps.core.models import Tramite, Turno, Area
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
        
        # No exponer fecha_nacimiento_date (es un objeto date) al JSON
        resp = {k: v for k, v in datos.items() if k != 'fecha_nacimiento_date'}
        return Response(resp)


class EmitirTurno(APIView):
    """
    POST  /api/turnos/emitir/
    Acepta: tramite_id, dni (opcional), es_embarazada (bool), es_discapacitado (bool)
    """
    def post(self, request):
        ser = TurnoEmitirSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        tramite = Tramite.objects.select_related("area").get(
            pk=ser.validated_data["tramite_id"]
        )
        dni = ser.validated_data.get("dni")
        es_embarazada = ser.validated_data.get("es_embarazada", False)
        es_discapacitado = ser.validated_data.get("es_discapacitado", False)

        try:
            turno = services.emitir_turno(
                tramite.area, tramite, dni,
                es_embarazada=es_embarazada,
                es_discapacitado=es_discapacitado,
            )
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
            "turno_id":   turno.id,
            "nombre":     nombre_visible,
            "tramite":    tramite.nombre,
            "espera":     espera,
            "prioridad":  turno.ticket.prioridad,
        })


class ConfiguracionAreaAPI(APIView):
    """
    GET /api/config/          → configuración del área por defecto
    GET /api/config/<area_id>/ → configuración de un área específica
    """
    def get(self, request, area_id=None):
        if area_id:
            area = Area.objects.filter(pk=area_id, activa=True).first()
        else:
            area = Area.objects.filter(activa=True).first()
        
        if not area:
            return Response({"detail": "Área no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        
        config = services.obtener_config_area(area)
        return Response(config)
