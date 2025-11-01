from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

class Enseignant(models.Model):
    SEXE_CHOICES = [('M', 'Masculin'), ('F', 'Féminin')]

    matricule = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=150)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    specialite = models.CharField(max_length=100)
    diplome = models.CharField(max_length=100)
    date_recrutement = models.DateField()
    statut = models.CharField(max_length=20, default='actif')
    photo = models.ImageField(upload_to='enseignants/', blank=True, null=True)
    matieres = models.ManyToManyField('matieres.Matiere', blank=True)

    # Trasabilité
    cree_par = models.ForeignKey(
        'utilisateurs.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enseignants_crees'
    )
    modifier_par = models.ForeignKey(
        'utilisateurs.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enseignants_modifies'
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('nom', 'prenom')  # Evite double enregistrement

    def clean(self):
        # Age minimum 18 ans
        if self.date_naissance:
            age = (date.today() - self.date_naissance).days // 365
            if age < 18:
                raise ValidationError("L'enseignant doit avoir au moins 18 ans.")

    def __str__(self):
        return f"{self.nom} {self.prenom}"
