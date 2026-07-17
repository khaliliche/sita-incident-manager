from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur


class UtilisateurAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informations métier', {'fields': ('role', 'zone', 'disponibilite')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations métier', {'fields': ('role', 'zone', 'disponibilite')}),
    )
    list_display = ('username', 'email', 'role', 'zone', 'disponibilite', 'is_staff')


admin.site.register(Utilisateur, UtilisateurAdmin)