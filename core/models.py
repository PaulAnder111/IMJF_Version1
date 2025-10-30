# core/models.py
from django.core.exceptions import ValidationError

class UniqueContactMixin:
    """Assure que téléphone et email sont uniques à travers toutes les apps."""

    def clean(self):
        super().clean()
        from utilisateurs.models import CustomUser
        from eleves.models import Eleve
        from enseignants.models import Enseignant

        # Vérifie unicité du téléphone
        if self.telephone:
            exists = (
                CustomUser.objects.filter(telephone=self.telephone).exclude(pk=self.pk).exists() or
                Eleve.objects.filter(telephone=self.telephone).exclude(pk=self.pk).exists() or
                Enseignant.objects.filter(telephone=self.telephone).exclude(pk=self.pk).exists()
            )
            if exists:
                raise ValidationError("Ce numéro de téléphone est déjà utilisé dans le système.")

        # Vérifie unicité du mail
        if self.email:
            exists = (
                CustomUser.objects.filter(email=self.email).exclude(pk=self.pk).exists() or
                Eleve.objects.filter(email=self.email).exclude(pk=self.pk).exists() or
                Enseignant.objects.filter(email=self.email).exclude(pk=self.pk).exists()
            )
            if exists:
                raise ValidationError("Cet email est déjà utilisé dans le système.")
