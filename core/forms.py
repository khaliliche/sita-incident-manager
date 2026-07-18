from django import forms
from .models import Zone, Equipement


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ['nom']


class EquipementForm(forms.ModelForm):
    class Meta:
        model = Equipement
        fields = ['nom']