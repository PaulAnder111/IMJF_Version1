# annee_scolaire/models.py
from django.db import models
from django.utils import timezone

class AnneeScolaireManager(models.Manager):
    def get_annee_courante(self):
        """Retourne l'année scolaire courante"""
        try:
            return self.get(est_annee_courante=True)
        except AnneeScolaire.DoesNotExist:
            return None

class AnneeScolaire(models.Model):
    nom = models.CharField(max_length=50, verbose_name="Nom de l'année scolaire")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    est_annee_courante = models.BooleanField(default=False, verbose_name="Année en cours")
    est_active = models.BooleanField(default=True, verbose_name="Active")
    
    objects = AnneeScolaireManager()
    
    class Meta:
        verbose_name = "Année scolaire"
        verbose_name_plural = "Années scolaires"
        ordering = ['-date_debut']
        db_table = 'annee_scolaire'  # Asire non tab la klè
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule année courante
        if self.est_annee_courante:
            AnneeScolaire.objects.exclude(pk=self.pk).update(est_annee_courante=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_annee_courante(cls):
        """Retourne l'année scolaire courante"""
        annee = cls.objects.get_annee_courante()
        if not annee:
            # Créer une année scolaire par défaut
            current_year = timezone.now().year
            annee = cls.objects.create(
                nom=f"{current_year}-{current_year + 1}",
                date_debut=timezone.now().date().replace(month=9, day=1),
                date_fin=timezone.now().date().replace(month=6, day=30, year=current_year + 1),
                est_annee_courante=True,
                est_active=True
            )
        return annee
    
    @property
    def est_terminee(self):
        """Vérifie si l'année scolaire est terminée"""
        return self.date_fin < timezone.now().date()
    
    @property
    def est_en_cours(self):
        """Vérifie si l'année scolaire est en cours"""
        today = timezone.now().date()
        return self.date_debut <= today <= self.date_fin