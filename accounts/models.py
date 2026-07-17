from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import Zone


class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('helpdesk', 'Agent Helpdesk'),
        ('technicien', 'Technicien'),
        ('ingenieur', 'Ingénieur'),
        ('superviseur', 'Superviseur'),
    ]
    DISPO_CHOICES = [
        ('disponible', 'Disponible'),
        ('occupe', 'Occupé'),
        ('absent', 'Absent'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    zone = models.ForeignKey(
        Zone, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='utilisateurs'
    )
    disponibilite = models.CharField(
        max_length=20, choices=DISPO_CHOICES, default='disponible',
        blank=True
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"