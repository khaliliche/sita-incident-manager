from django import forms
from .models import Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['compagnie_aerienne', 'numero_vol', 'description', 'zone', 'equipement', 'priorite']


class ReaffectationForm(forms.Form):
    ingenieur = forms.ModelChoiceField(
        queryset=None,
        label="Réaffecter à",
        empty_label="— Choisir un ingénieur —"
    )

    def __init__(self, *args, zone=None, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import Utilisateur
        qs = Utilisateur.objects.filter(role='ingenieur')
        if zone:
            qs = qs.filter(zone=zone)
        self.fields['ingenieur'].queryset = qs.order_by('-disponibilite', 'username')