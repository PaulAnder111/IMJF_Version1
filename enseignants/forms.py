# enseignants/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import Enseignant
from core.validators import validate_phone_prefix  # Retire validate_unique_across_models

class EnseignantForm(forms.ModelForm):
    class Meta:
        model = Enseignant
        fields = [
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
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Nom de famille'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Prénom'
            }),
            'sexe': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500'
            }),
            'date_naissance': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500'
            }),
            'lieu_naissance': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Lieu de naissance'
            }),
            'adresse': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Adresse complète'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': '+509 XXXX XXXX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'exemple@email.com'
            }),
            'specialite': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Ex: Mathématiques, Français...'
            }),
            'diplome': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'placeholder': 'Ex: Licence, Master...'
            }),
            'date_recrutement': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500'
            }),
            'statut': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500',
                'accept': 'image/*'
            }),
            'matieres': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-2'
            }),
        }

        labels = {
            'nom': 'Nom *',
            'prenom': 'Prénom *',
            'sexe': 'Sexe *',
            'date_naissance': 'Date de naissance *',
            'lieu_naissance': 'Lieu de naissance *',
            'adresse': 'Adresse *',
            'telephone': 'Téléphone *',
            'email': 'Email *',
            'specialite': 'Spécialité *',
            'diplome': 'Diplôme *',
            'date_recrutement': 'Date de recrutement *',
            'statut': 'Statut',
            'photo': 'Photo',
            'matieres': 'Matières enseignées',
        }

    # ----------------------- VALIDATIONS SIMPLIFIÉES -----------------------

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Valide sèlman inik nan menm modèl Enseignant
            queryset = Enseignant.objects.filter(email__iexact=email)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError("Un enseignant avec cet email existe déjà.")
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            validate_phone_prefix(telephone)
            # Valide sèlman inik nan menm modèl Enseignant
            queryset = Enseignant.objects.filter(telephone=telephone)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError("Un enseignant avec ce numéro de téléphone existe déjà.")
        return telephone