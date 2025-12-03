from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Matiere(models.Model):
    code_matiere = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
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
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="matieres_cree"
    )
    modifier_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="matieres_modifie"
    )

    # --------------- CODE MATIERE OTOMATIK ---------------
    def generate_code_matiere(self):
        """
        Code Matière format : MAT-2025-0001
        """
        from datetime import date
        prefix = "MAT"
        year = date.today().year
        last_matiere = Matiere.objects.order_by('-id').first()
        next_id = (last_matiere.id + 1) if last_matiere else 1
        return f"{prefix}-{year}-{next_id:04d}"

    def save(self, *args, **kwargs):
        if not self.code_matiere:
            self.code_matiere = self.generate_code_matiere()
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['nom_matiere']

    def clean(self):
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
    user = models.ForeignKey(
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