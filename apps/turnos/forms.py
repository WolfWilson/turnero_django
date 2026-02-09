# apps/turnos/forms.py
from django import forms
from apps.core.models import Tramite

class SolicitudTurnoForm(forms.Form):
    dni = forms.CharField(
        label="DNI (opcional)",
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ej.: 12345678"}),
    )
    tramite = forms.ModelChoiceField(
        queryset=Tramite.objects.filter(activa=True),
        empty_label="Seleccione el trámite",
        label="Trámite / Motivo",
    )
