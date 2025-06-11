# apps/turnos/forms.py
from django import forms
from apps.core.models import Categoria

class SolicitudTurnoForm(forms.Form):
    dni = forms.CharField(
        label="DNI (opcional)",
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ej.: 12345678"}),
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        empty_label="Seleccione el trámite",
        label="Categoría / Motivo",
    )
