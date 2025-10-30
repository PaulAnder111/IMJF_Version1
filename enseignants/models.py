# enseignants/models.py
from django.db import models
from django.utils import timezone
from core.models import UniqueContactMixin

class Enseignant(UniqueContactMixin, models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('archive', 'Archivé'),
    ]

    matricule = models.CharField(max_length=30, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=100, null=True, blank=True)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    telephone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    specialite = models.CharField(max_length=150, null=True, blank=True)
    diplome = models.CharField(max_length=150, null=True, blank=True)
    date_recrutement = models.DateField(default=timezone.now)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    photo = models.ImageField(upload_to='enseignants/photos/', null=True, blank=True)
   
 # Relasyon ManyToMany avèk Matiere
    matieres = models.ManyToManyField(
        'matieres.Matiere',
        blank=True,
        related_name='enseignants',
        verbose_name="Matières enseignées")
   
    class Meta:
        verbose_name = "Enseignant"
        verbose_name_plural = "Enseignants"

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.matricule}"