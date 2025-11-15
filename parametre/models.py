from django.db import models
from django.conf import settings

class HistoriqueAction(models.Model):
    ACTION_CHOICES = [
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
        ('connexion', 'Connexion'),
        ('deconnexion', 'Déconnexion'),
        ('autre', 'Autre'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)  # ex: "Cours", "Eleve"
    object_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historique Action"
        verbose_name_plural = "Historique Actions"
        ordering = ['-date_action']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} ({self.object_id})"
