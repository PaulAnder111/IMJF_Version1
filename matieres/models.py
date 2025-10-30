# matieres/models.py

from django.db import models

class Matiere(models.Model):
    code_matiere = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code Matière"
    )
    nom_matiere = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom de la Matière"
    )
    heure_hebdomadaire = models.PositiveIntegerField(
        default=0,
        verbose_name="Heures Hebdomadaires"
    )
    statut = models.CharField(
        max_length=20,
        choices=[('actif', 'Actif'), ('inactif', 'Inactif')],
        default='actif'
    )

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['nom_matiere']

    def __str__(self):
        return f"{self.code_matiere} - {self.nom_matiere}"