from rest_framework import serializers

class TurnoEmitirSerializer(serializers.Serializer):
    tramite_id       = serializers.IntegerField()
    dni              = serializers.IntegerField(required=False,
                                                min_value=1_000_000,
                                                max_value=99_999_999)
    es_embarazada    = serializers.BooleanField(required=False, default=False)
    es_discapacitado = serializers.BooleanField(required=False, default=False)


class BuscarPersonaSerializer(serializers.Serializer):
    dni = serializers.IntegerField(
        min_value=1_000_000,
        max_value=99_999_999,
        help_text="DNI de 7 u 8 dígitos",
    )
