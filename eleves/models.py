# eleves/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
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
        # Validate model before saving to enforce cross-model constraints
        try:
            self.full_clean()
        except ValidationError:
            raise
        super().save(*args, **kwargs)


# Custom manager: by default exclude archived ('radié') students
class ActiveEleveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(statut='radié')

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

    # Managers: `objects` returns active (non-radié) by default; `all_objects` returns everything
    objects = ActiveEleveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"
        unique_together = ['matricule', 'annee_scolaire']
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'prenom', 'date_naissance', 'annee_scolaire'],
                name='unique_eleve_person_year'
            )
        ]

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.matricule}"

    def save(self, *args, **kwargs):
        if not self.annee_scolaire_id:
            self.annee_scolaire = AnneeScolaire.get_annee_courante()
        # Run model validation before saving to enforce business rules
        try:
            self.full_clean()
        except ValidationError:
            raise
        # Wrap save in a transaction to catch DB-level unique constraint violations
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except IntegrityError:
            raise ValidationError("Erreur de sauvegarde : un élève avec les mêmes informations existe déjà.")

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

    def clean(self):
        """Prevent creating an Eleve when the same person exists as an Enseignant."""
        if self.nom and self.prenom and self.date_naissance:
            try:
                from enseignants.models import Enseignant
                if Enseignant.objects.filter(
                    nom__iexact=self.nom.strip(),
                    prenom__iexact=self.prenom.strip(),
                    date_naissance=self.date_naissance
                ).exists():
                    raise ValidationError("Impossible de créer l'élève : cette personne est enregistrée comme enseignant.")
            except ImportError:
                # If enseignants app not available, skip the check
                pass
        # Prevent duplicate Eleve for the same school year (same person)
        if self.annee_scolaire_id:
            # normalize names
            nom_norm = (self.nom or '').strip()
            prenom_norm = (self.prenom or '').strip()
            # Use all_objects to include archived records in duplicate detection
            qs = Eleve.all_objects.filter(
                nom__iexact=nom_norm,
                prenom__iexact=prenom_norm,
                date_naissance=self.date_naissance,
                annee_scolaire=self.annee_scolaire
            ).exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("Un élève avec ces informations existe déjà pour cette année scolaire.")

        # Age-based rules by niveau (same rules as Inscription)
        try:
            ref_date = self.date_inscription or timezone.now().date()
        except Exception:
            ref_date = timezone.now().date()

        def _age(birth, ref):
            years = ref.year - birth.year
            if (ref.month, ref.day) < (birth.month, birth.day):
                years -= 1
            return years

        age = _age(self.date_naissance, ref_date)
        niveau_val = (self.niveau or '').strip().lower()

        if any(x in niveau_val for x in ['7', '7eme', '7ème', 'sept']):
            if age < 11:
                raise ValidationError("Âge invalide : un élève de 7ème doit avoir au moins 11 ans.")
        if 'nsi' in niveau_val:
            if age < 15:
                raise ValidationError("Âge invalide : NSI nécessite au moins 15 ans.")
        if 'nsii' in niveau_val:
            if age < 16:
                raise ValidationError("Âge invalide : NSII nécessite au moins 16 ans.")
        if 'nsiv' in niveau_val:
            if age < 17:
                raise ValidationError("Âge invalide : NSIV nécessite au moins 17 ans.")