# cours/models.py

from django.db import models

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

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        constraints = [
            models.UniqueConstraint(
                fields=['classe', 'jour', 'heure_debut'],
                name='unique_classe_creneau'
            ),
            models.UniqueConstraint(
                fields=['enseignant', 'jour', 'heure_debut'],
                name='unique_enseignant_creneau'
            )
        ]

    def __str__(self):
        return f"{self.matiere.nom_matiere} → {self.classe.nom_classe} ({self.jour})"