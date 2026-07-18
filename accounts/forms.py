from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur


class UtilisateurCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'zone', 'disponibilite']


class UtilisateurEditForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'email', 'role', 'zone', 'disponibilite', 'is_active']