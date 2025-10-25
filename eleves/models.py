from django.db import models
from django.utils import timezone

class Eleve(models.Model):
    matricule = models.CharField(max_length=50, unique=True, verbose_name="Matricule")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=255)
    sexe = models.CharField(
        max_length=10,
        choices=[('M', 'Masculin'), ('F', 'Féminin')]
    )
    adresse = models.TextField()
    niveau = models.CharField(max_length=50)
    classe_actuelle = models.ForeignKey(
        'classes.Classe',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eleves_actuels'
    )
    statut = models.CharField(
        max_length=20,
        default='actif',
        choices=[('actif', 'Actif'), ('radié', 'Radié'), ('suspendu', 'Suspendu')]
    )
    photo = models.ImageField(
        upload_to='eleves/photos/',
        blank=True,
        null=True,
        default='eleves/photos/default_avatar.png',
        verbose_name="Photo"
    )
    date_inscription = models.DateField(
        default=timezone.now,  # ← Sa pral evite erè a
        verbose_name="Date d'inscription"
    )

    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.matricule}"