# classes/models.py
from django.db import models

class Classe(models.Model):
    NIVEAU_CHOICES = [
        ('7ème', '7ème'),
        ('8ème', '8ème'),
        ('9ème', '9ème'),
        ('NSI', 'NSI'),
        ('NSII', 'NSII'),
        ('NSIII', 'NSIII'),
        ('NSIV', 'NSIV'),
    ]
    
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
    ]

    code_classe = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code Classe"
    )
    nom_classe = models.CharField(
        max_length=100,
        verbose_name="Nom de la classe"
    )
    niveau = models.CharField(
        max_length=20,
        choices=NIVEAU_CHOICES,
        verbose_name="Niveau scolaire"
    )
    
    capacite_max = models.PositiveIntegerField(
        default=50,
        verbose_name="Capacité maximale"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='actif',
        verbose_name="Statut"
    )

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ['niveau', 'nom_classe']

    def __str__(self):
        return f"{self.nom_classe} ({self.niveau})"