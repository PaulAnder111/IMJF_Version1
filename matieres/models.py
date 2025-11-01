from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

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

    # ✅ Tracabilité
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # <<< chanjman la
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="matieres_cree"
    )
    modifier_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # <<< chanjman la tou
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="matieres_modifie"
    )

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['nom_matiere']

    def clean(self):
        # 🔹 Vérification doublon (sécurisé même si unique=True)
        if Matiere.objects.filter(code_matiere=self.code_matiere).exclude(id=self.id).exists():
            raise ValidationError({"code_matiere": f"Le code {self.code_matiere} est déjà utilisé."})
        if Matiere.objects.filter(nom_matiere__iexact=self.nom_matiere).exclude(id=self.id).exists():
            raise ValidationError({"nom_matiere": f"Le nom {self.nom_matiere} est déjà utilisé."})

    def __str__(self):
        return f"{self.code_matiere} - {self.nom_matiere}"


# ✅ Historique de Matières
class HistoriqueMatiere(models.Model):
    ACTIONS = [
        ('Création', 'Création'),
        ('Modification', 'Modification'),
        ('Suppression', 'Suppression'),
    ]
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name="historique")
    action = models.CharField(max_length=20, choices=ACTIONS)
    user = models.ForeignKey(  # <<< chanjman la
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    description = models.TextField(blank=True)
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historique Matière"
        verbose_name_plural = "Historique Matières"
        ordering = ['-date_action']

    def __str__(self):
        return f"{self.action} - {self.matiere.nom_matiere} ({self.date_action.strftime('%Y-%m-%d %H:%M')})"
