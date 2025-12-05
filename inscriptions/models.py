from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from classes.models import Classe
from utilisateurs.models import CustomUser
from eleves.models import Eleve
from core.models import BaseModel


class HistoriqueClasses(models.Model):
    eleve = models.ForeignKey('eleves.Eleve', on_delete=models.CASCADE, related_name='historique_classes')
    classe = models.ForeignKey('classes.Classe', on_delete=models.SET_NULL, null=True)
    annee_scolaire = models.CharField(max_length=9)
    # When the history period starts and ends
    date_debut = models.DateField(default=timezone.now)
    date_fin = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Historique de Classe"
        verbose_name_plural = "Historiques de Classes"
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.eleve.nom} {self.eleve.prenom} → {self.classe.nom_classe} ({self.annee_scolaire})"


class Inscription(BaseModel):
    """
    Représente une inscription scolaire d'un élève pour une année donnée.
    Gère automatiquement l'historique des classes et évite les doublons.
    """

    # === Informations personnelles ===
    nom = models.CharField(max_length=100, verbose_name="Nom de l'élève")
    prenom = models.CharField(max_length=100, verbose_name="Prénom de l'élève")
    date_naissance = models.DateField(verbose_name="Date de naissance")
    lieu_naissance = models.CharField(max_length=255, verbose_name="Lieu de naissance")
    sexe = models.CharField(max_length=10, choices=[('M', 'Masculin'), ('F', 'Féminin')], verbose_name="Sexe")
    adresse = models.TextField(verbose_name="Adresse complète")
    niveau = models.CharField(max_length=50, verbose_name="Niveau scolaire")

    # === Informations académiques ===
    classe = models.ForeignKey(
        Classe, on_delete=models.PROTECT, related_name='inscriptions', verbose_name="Classe choisie"
    )
    annee_scolaire = models.CharField(max_length=9, help_text="Format: AAAA-AAAA", verbose_name="Année scolaire")
    date_inscription = models.DateField(auto_now_add=True)

    # === Informations du responsable ===
    personne_responsable = models.CharField(max_length=255, verbose_name="Nom du responsable")
    profession_responsable = models.CharField(max_length=100, verbose_name="Profession du responsable")
    telephone_responsable = models.CharField(max_length=20, verbose_name="Téléphone du responsable")
    email_responsable = models.EmailField(blank=True, null=True, verbose_name="Email du responsable")

    # === Informations optionnelles ===
    ecole_origine = models.CharField(max_length=255, blank=True, null=True, verbose_name="École d'origine")

    # === Statut inscription ===
    statut = models.CharField(
        max_length=20,
        choices=[
            ('pre-inscrit', 'Pré-inscrit'),
            ('validé', 'Validé'),
            ('actif', 'Actif'),
            ('refuse', 'Refusé'),
        ],
        default='pre-inscrit',
        verbose_name="Statut de l'inscription"
    )

    # === Références système ===
    cree_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='inscriptions_crees')
    eleve = models.OneToOneField(Eleve, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Élève lié (si validé)")

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = ('nom', 'prenom', 'date_naissance', 'annee_scolaire')
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.prenom} {self.nom} → {self.classe.nom_classe} ({self.annee_scolaire})"

    # === Logique métier principale ===
    def save(self, *args, **kwargs):
        from inscriptions.models import HistoriqueClasses  # evite circular import
        # Ensure model validations run even when saving programmatically
        try:
            self.full_clean()
        except ValidationError:
            # Re-raise so callers can catch or so Django surfaces errors
            raise

        # Empêcher double inscription d'un élève dans la même année
        if Inscription.objects.filter(
            nom__iexact=self.nom.strip(),
            prenom__iexact=self.prenom.strip(),
            date_naissance=self.date_naissance,
            annee_scolaire=self.annee_scolaire
        ).exclude(id=self.id).exists():
            raise ValueError(f"L'élève {self.prenom} {self.nom} est déjà inscrit pour l'année {self.annee_scolaire}.")

        # Enregistrement normal
        super().save(*args, **kwargs)

        # Si l'élève existe, gérer l'historique automatiquement
        if self.eleve:
            # Fermer les anciens historiques pour la même année
            HistoriqueClasses.objects.filter(
                eleve=self.eleve,
                annee_scolaire=self.annee_scolaire,
                date_fin__isnull=True
            ).update(date_fin=timezone.now().date())

            # Créer un nouvel historique si inexistant
            HistoriqueClasses.objects.get_or_create(
                eleve=self.eleve,
                classe=self.classe,
                annee_scolaire=self.annee_scolaire,
                defaults={'date_debut': timezone.now().date()}
            )

    def clean(self):
        """
        Model-level validation to prevent:
        - registering a person already present as an Enseignant
        - duplicate inscription for same person/year
        - registering a person already an Eleve for the same school year
        """
        # avoid circular imports at module import time
        from enseignants.models import Enseignant
        from eleves.models import Eleve

        if self.nom and self.prenom and self.date_naissance:
            # 1) Person already a teacher?
            if Enseignant.objects.filter(
                nom__iexact=self.nom.strip(),
                prenom__iexact=self.prenom.strip(),
                date_naissance=self.date_naissance
            ).exists():
                raise ValidationError("Impossible d'enregistrer : cette personne est déjà enregistrée comme enseignant.")

            # 2) Duplicate inscription for same year
            if Inscription.objects.filter(
                nom__iexact=self.nom.strip(),
                prenom__iexact=self.prenom.strip(),
                date_naissance=self.date_naissance,
                annee_scolaire=self.annee_scolaire
            ).exclude(pk=self.pk).exists():
                raise ValidationError("L'élève est déjà inscrit pour cette année scolaire.")

            # 3) Person already an Eleve with history for that year
            eleve_qs = Eleve.objects.filter(
                nom__iexact=self.nom.strip(),
                prenom__iexact=self.prenom.strip(),
                date_naissance=self.date_naissance
            )
            if eleve_qs.exists():
                eleve = eleve_qs.first()
                from inscriptions.models import HistoriqueClasses as HC
                if HC.objects.filter(eleve=eleve, annee_scolaire=self.annee_scolaire).exists():
                    raise ValidationError("Cet élève est déjà inscrit pour cette année scolaire.")
            # === Age-based rules by niveau ===
            # Compute reference date for age calculation: use date_inscription if present, else today
            try:
                ref_date = self.date_inscription or timezone.now().date()
            except Exception:
                ref_date = timezone.now().date()

            # Helper: compute age in years at ref_date
            def _age(birth, ref):
                years = ref.year - birth.year
                if (ref.month, ref.day) < (birth.month, birth.day):
                    years -= 1
                return years

            age = _age(self.date_naissance, ref_date)

            niveau_val = (self.niveau or '').strip().lower()
            # 7ème année should be at least 11 years old
            if any(x in niveau_val for x in ['7', '7eme', '7ème', 'sept']):
                if age < 11:
                    raise ValidationError("Âge invalide : un élève de 7ème doit avoir au moins 11 ans.")

            # NSI / NSII / NSIV rules
            if 'nsi' in niveau_val:
                if age < 15:
                    raise ValidationError("Âge invalide : NSI nécessite au moins 15 ans.")
            if 'nsii' in niveau_val or 'nsii' in (self.niveau or '').lower():
                if age < 16:
                    raise ValidationError("Âge invalide : NSII nécessite au moins 16 ans.")
            if 'nsiv' in niveau_val:
                if age < 17:
                    raise ValidationError("Âge invalide : NSIV nécessite au moins 17 ans.")
