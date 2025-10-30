from django.db import models
from classes.models import Classe
from utilisateurs.models import CustomUser
from eleves.models import Eleve

class Inscription(models.Model):
    # === Enfòmasyon eleve a (sòt dokiman an) ===
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de l'élève"
    )
    prenom = models.CharField(
        max_length=100,
        verbose_name="Prénom de l'élève"
    )
    date_naissance = models.DateField(
        verbose_name="Date de naissance"
    )
    lieu_naissance = models.CharField(
        max_length=255,
        verbose_name="Lieu de naissance"
    )
    sexe = models.CharField(
        max_length=10,
        choices=[('M', 'Masculin'), ('F', 'Féminin')],
        verbose_name="Sexe"
    )
    adresse = models.TextField(
        verbose_name="Adresse complète (rue, commune, département)"
    )
    niveau = models.CharField(
        max_length=50,
        verbose_name="Niveau scolaire"
    )

    # === Enfòmasyon akademik ===
    classe = models.ForeignKey(
        Classe,
        on_delete=models.PROTECT,
        related_name='inscriptions',
        verbose_name="Classe choisie"
    )
    annee_scolaire = models.CharField(
        max_length=9,
        help_text="Format: AAAA-AAAA (ex: 2025-2026)",
        verbose_name="Année scolaire"
    )

    # === Enfòmasyon paran/titilè ===
    personne_responsable = models.CharField(
        max_length=255,
        verbose_name="Nom de la personne responsable"
    )
    profession_responsable = models.CharField(
        max_length=100,
        verbose_name="Profession du responsable"
    )
    telephone_responsable = models.CharField( unique= True,
        max_length=20,
        verbose_name="Téléphone du responsable"
    )
    email_responsable = models.EmailField( unique=True,
        blank=True,
        null=True,
        verbose_name="Email du responsable (optionnel)"
    )

    # === Enfòmasyon opsyonèl ===
    ecole_origine = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="École d'origine (optionnel)"
    )

    # === Sistèm ak jesion pwosesis ===
    date_inscription = models.DateField(
        auto_now_add=True,
        verbose_name="Date d'inscription"
    )
    statut = models.CharField(
        max_length=20,
        choices=[
            ('pre-inscrit', 'Pré-inscrit'),
            ('validé', 'Validé'),
            ('aktif', 'Actif'),
            ('refize', 'Refusé'),
        ],
        default='pre-inscrit',
        verbose_name="Statut de l'inscription"
    )
    cree_par = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inscriptions_crees',
        verbose_name="Créé par (secrétaire)"
    )

    # === Relasyon avèk Eleve (lè enskripsyon an valide) ===
    eleve = models.OneToOneField(
        Eleve,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Élève créé (si validé)",
        help_text="lier avec les dossiers de l'eleves si les inscription sont valide."
    )

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = ('nom', 'prenom', 'date_naissance', 'annee_scolaire')
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.prenom} {self.nom} → {self.classe} ({self.annee_scolaire})"