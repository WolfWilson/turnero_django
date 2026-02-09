from rest_framework import serializers

class TurnoEmitirSerializer(serializers.Serializer):
    tramite_id = serializers.IntegerField()
    dni        = serializers.IntegerField(required=False,
                                          min_value=10_000_000,
                                          max_value=99_999_999)


class BuscarPersonaSerializer(serializers.Serializer):
    dni = serializers.IntegerField(
        min_value=10_000_000,
        max_value=99_999_999,
        help_text="DNI de 8 dígitos",
    )
