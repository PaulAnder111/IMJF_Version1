# enseignants/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import Enseignant

class EnseignantForm(forms.ModelForm):
    class Meta:
        model = Enseignant
        fields = [
            'matricule',
            'nom',
            'prenom',
            'sexe',
            'date_naissance',
            'lieu_naissance',
            'adresse',
            'telephone',
            'email',
            'specialite',
            'diplome',
            'date_recrutement',
            'statut',
            'photo',
            'matieres'
        ]
        widgets = {
            'matieres': forms.CheckboxSelectMultiple(),
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'date_recrutement': forms.DateInput(attrs={'type': 'date'}),
            'statut': forms.Select(),
            'sexe': forms.Select(),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verifye sèlman nan Enseignant
            if Enseignant.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Cet email est déjà utilisé par un enseignant.")
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            # Verifye sèlman nan Enseignant
            if Enseignant.objects.filter(telephone=telephone).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Ce numéro est déjà utilisé par un enseignant.")
        return telephone