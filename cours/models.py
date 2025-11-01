from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

class Cours(models.Model):
    JOURS = [
        ('Lundi', 'Lundi'),
        ('Mardi', 'Mardi'),
        ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'),
        ('Vendredi', 'Vendredi'),
        ('Samedi', 'Samedi'),
    ]

    matiere = models.ForeignKey('matieres.Matiere', on_delete=models.CASCADE, verbose_name="Matière")
    classe = models.ForeignKey('classes.Classe', on_delete=models.CASCADE, verbose_name="Classe")
    enseignant = models.ForeignKey('enseignants.Enseignant', on_delete=models.CASCADE, verbose_name="Enseignant")
    jour = models.CharField(max_length=10, choices=JOURS, verbose_name="Jour")
    heure_debut = models.TimeField(verbose_name="Heure de début")
    heure_fin = models.TimeField(verbose_name="Heure de fin")
    salle = models.CharField(max_length=20, blank=True, verbose_name="Salle")
    statut = models.CharField(max_length=20, default='actif', verbose_name="Statut")

    # 🔒 Trasabilité
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='cours_crees')
    modifier_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='cours_modifies')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"

    def clean(self):
        # 1️⃣ Vérifie chevauchement pour enseignant
        chevauchement_enseignant = Cours.objects.filter(
            enseignant=self.enseignant,
            jour=self.jour
        ).exclude(id=self.id).filter(
            heure_debut__lt=self.heure_fin,
            heure_fin__gt=self.heure_debut
        )
        if chevauchement_enseignant.exists():
            raise ValidationError(
                {"enseignant": f"L'enseignant {self.enseignant} a déjà un cours pendant cette période ({self.jour})."}
            )

        # 2️⃣ Vérifie chevauchement pour classe
        chevauchement_classe = Cours.objects.filter(
            classe=self.classe,
            jour=self.jour
        ).exclude(id=self.id).filter(
            heure_debut__lt=self.heure_fin,
            heure_fin__gt=self.heure_debut
        )
        if chevauchement_classe.exists():
            raise ValidationError(
                {"classe": f"La classe {self.classe} a déjà un autre cours pendant cette période ({self.jour})."}
            )

    def __str__(self):
        return f"{self.matiere.nom_matiere} → {self.classe.nom_classe} ({self.jour})"


# -------------------- Historique des cours --------------------
class HistoriqueCours(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='historique')
    action = models.CharField(max_length=50)  # ex: "Création", "Modification", "Suppression"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_action = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Historique Cours"
        verbose_name_plural = "Historique Cours"
        ordering = ['-date_action']

    def __str__(self):
        return f"{self.action} - {self.cours} par {self.user}"
