from django.db import models
from django.conf import settings
from core.models import Zone, Equipement


class Ticket(models.Model):
    PRIORITE_CHOICES = [
        ('P1', 'P1'),
        ('P2', 'P2'),
        ('P3', 'P3'),
        ('P4', 'P4'),
        ('P5', 'P5'),
    ]
    STATUT_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('affecte', 'Affecté'),
        ('en_cours', 'En cours de traitement'),
        ('escalade', 'Escaladé'),
        ('resolu', 'Résolu'),
        ('cloture', 'Clôturé'),
    ]

    compagnie_aerienne = models.CharField(max_length=100)
    numero_vol = models.CharField(max_length=20)
    description = models.TextField()

    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name='tickets')
    equipement = models.ForeignKey(Equipement, on_delete=models.PROTECT, related_name='tickets')
    priorite = models.CharField(max_length=2, choices=PRIORITE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ouvert')

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='tickets_crees'
    )
    assigne_a = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tickets_assignes'
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_cloture = models.DateTimeField(null=True, blank=True)
    commentaire_cloture = models.TextField(blank=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.priorite} - {self.get_statut_display()}"


class TicketHistorique(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='historique')
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    action = models.CharField(max_length=100)
    ancien_statut = models.CharField(max_length=20, blank=True)
    nouveau_statut = models.CharField(max_length=20, blank=True)
    commentaire = models.TextField(blank=True)
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_action']

    def __str__(self):
        return f"{self.ticket} - {self.action} - {self.date_action}"