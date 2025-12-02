# eleves/models.py
from django.db import models
from django.utils import timezone
from classes.models import Classe
from annee_scolaire.models import AnneeScolaire  # Import depi nouvo aplikasyon

# Retire modèl AnneeScolaire ki te la deja

class HistoriqueEleve(models.Model):
    ACTIONS = [
        ('inscription', 'Nouvelle inscription'),
        ('changement_classe', 'Changement de classe'),
        ('suspension', 'Suspension'),
        ('reprise', 'Reprise des cours'),
        ('graduation', 'Diplômé'),
        ('discipline', 'Mesure disciplinaire'),
        ('autre', 'Autre'),
    ]

    eleve = models.ForeignKey('Eleve', on_delete=models.CASCADE, related_name='historique_eleves')
    action = models.CharField(max_length=50, choices=ACTIONS)
    description = models.TextField()
    date_action = models.DateTimeField(default=timezone.now)
    effectue_par = models.ForeignKey('utilisateurs.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    annee_scolaire = models.ForeignKey(
        AnneeScolaire, 
        on_delete=models.CASCADE,
        default=AnneeScolaire.get_annee_courante
    )

    def __str__(self):
        return f"{self.eleve.nom} - {self.get_action_display()} ({self.date_action.strftime('%Y-%m-%d')})"
    
    def save(self, *args, **kwargs):
        if not self.annee_scolaire_id:
            self.annee_scolaire = AnneeScolaire.get_annee_courante()
        super().save(*args, **kwargs)

class Eleve(models.Model):
    matricule = models.CharField(max_length=50, verbose_name="Matricule")
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
        verbose_name="Photo"
    )
    date_inscription = models.DateField(
        default=timezone.now,
        verbose_name="Date d'inscription"
    )
    annee_scolaire = models.ForeignKey(
        AnneeScolaire,
        on_delete=models.CASCADE,
        verbose_name="Année scolaire",
        null=True,
        blank=True,
        related_name='eleves'
    )

    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"
        unique_together = ['matricule', 'annee_scolaire']

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.matricule}"

    def save(self, *args, **kwargs):
        if not self.annee_scolaire_id:
            self.annee_scolaire = AnneeScolaire.get_annee_courante()
        super().save(*args, **kwargs)

    @property
    def initial(self):
        """Retounen premye lèt non ak prenom eleve a"""
        first_initial = self.prenom[0].upper() if self.prenom and self.prenom.strip() else ""
        last_initial = self.nom[0].upper() if self.nom and self.nom.strip() else ""
        
        if first_initial and last_initial:
            return f"{first_initial}{last_initial}"
        elif first_initial:
            return first_initial
        elif last_initial:
            return last_initial
        elif self.matricule and self.matricule.strip():
            return self.matricule[0].upper()
        else:
            return "E"