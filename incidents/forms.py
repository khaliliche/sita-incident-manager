from django import forms
from .models import Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['compagnie_aerienne', 'numero_vol', 'description', 'zone', 'equipement', 'priorite']