from django.db import models
from django.core.exceptions import ValidationError
from datetime import date


class Enseignant(models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin')
    ]
    
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('archive', 'Archivé'),
        ('conge', 'En congé'),
    ]

    # Matricule otomatik (pa antre nan form)
    matricule = models.CharField(
        max_length=20,
        unique=True,
        blank=True,              # obligatwa pou sa mache
        verbose_name="Matricule"
    )

    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, verbose_name="Sexe")
    date_naissance = models.DateField(verbose_name="Date de naissance")
    lieu_naissance = models.CharField(max_length=150, verbose_name="Lieu de naissance")
    adresse = models.CharField(max_length=255, verbose_name="Adresse")
    telephone = models.CharField(max_length=20, unique=True, verbose_name="Téléphone")
    email = models.EmailField(unique=True, verbose_name="Email")
    specialite = models.CharField(max_length=100, verbose_name="Spécialité")
    diplome = models.CharField(max_length=100, verbose_name="Diplôme")
    date_recrutement = models.DateField(verbose_name="Date de recrutement")
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='actif',
        verbose_name="Statut"
    )
    photo = models.ImageField(
        upload_to='enseignants/',
        blank=True,
        null=True,
        verbose_name="Photo"
    )
    matieres = models.ManyToManyField(
        'matieres.Matiere',
        blank=True,
        verbose_name="Matières enseignées"
    )

    # Traçabilité
    cree_par = models.ForeignKey(
        'utilisateurs.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enseignants_crees',
        verbose_name="Créé par"
    )
    modifier_par = models.ForeignKey(
        'utilisateurs.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enseignants_modifies',
        verbose_name="Modifié par"
    )
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Enseignant"
        verbose_name_plural = "Enseignants"
        ordering = ['nom', 'prenom']
        unique_together = ('nom', 'prenom')  # Evite doublon

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.specialite})"

    @property
    def initial(self):
        """Retounen premye lèt non ak prenom enseignant la (pou inisyal avatar - style WhatsApp)."""
        first_initial = self.prenom[0].upper() if self.prenom and self.prenom.strip() else ""
        last_initial = self.nom[0].upper() if self.nom and self.nom.strip() else ""
        
        # Return both initials if available
        if first_initial and last_initial:
            return f"{first_initial}{last_initial}"
        elif first_initial:
            return first_initial
        elif last_initial:
            return last_initial
        elif self.matricule and self.matricule.strip():
            return self.matricule[0].upper()
        else:
            return "T"  # Default fallback for Teacher (Enseignant)

    # --------------- VALIDATION GENERALE ---------------
    def clean(self):

        # Age minimum 18 ans
        if self.date_naissance:
            age = (date.today() - self.date_naissance).days // 365
            if age < 18:
                raise ValidationError("L'enseignant doit avoir au moins 18 ans.")

        # Date recrutement ne peut pas être dans le futur
        if self.date_recrutement and self.date_recrutement > date.today():
            raise ValidationError("La date de recrutement ne peut pas être dans le futur.")

        # Vérifier si pas déjà élève
        try:
            from eleves.models import Eleve
            if self.date_naissance and Eleve.objects.filter(
                nom__iexact=self.nom.strip(),
                prenom__iexact=self.prenom.strip(),
                date_naissance=self.date_naissance
            ).exists():
                raise ValidationError("Cette personne est déjà enregistrée comme élève.")
        except Exception:
            pass

    # --------------- MATRICULE AUTOMATIQUE ---------------
    def generate_matricule(self):
        """
        Matricule format : ENS-2025-0001
        """
        prefix = "ENS"
        year = date.today().year

        last_teacher = Enseignant.objects.order_by('-id').first()
        next_id = (last_teacher.id + 1) if last_teacher else 1

        return f"{prefix}-{year}-{next_id:04d}"

    def save(self, *args, **kwargs):
        # Génère matricule si vide
        if not self.matricule:
            self.matricule = self.generate_matricule()

        self.full_clean()  # Validation complète
        super().save(*args, **kwargs)

    # --------------- PROPRIETES UTILES ---------------
    def __str__(self):
        return f"{self.nom} {self.prenom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def age(self):
        if self.date_naissance:
            return (date.today() - self.date_naissance).days // 365
        return None
