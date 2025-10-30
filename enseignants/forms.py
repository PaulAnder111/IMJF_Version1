# enseignants/forms.py

from django import forms
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
            'matricule': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500',
                'placeholder': 'Ex: ENS2025001'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500',
                'placeholder': 'Entrez le nom'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500',
                'placeholder': 'Entrez le prénom'
            }),
            'sexe': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500'
            }),
            'date_naissance': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500',
                'type': 'date'
            }),
            'lieu_naissance': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500',
                'placeholder': 'Ex: Port-au-Prince'
            }),
            'adresse': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500',
                'placeholder': 'Adresse complète'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500',
                'placeholder': '+509 XXXX-XXXX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500',
                'placeholder': 'exemple@email.com'
            }),
            'specialite': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500',
                'placeholder': 'Ex: Mathématiques'
            }),
            'diplome': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500',
                'placeholder': 'Ex: Licence en Mathématiques'
            }),
            'date_recrutement': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500',
                'type': 'date'
            }),
            'statut': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gold-500'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 text-gray-500'
            }),
            'matieres': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-2 mt-2'
            }),
        }
        labels = {
            'matricule': 'Matricule *',
            'nom': 'Nom *',
            'prenom': 'Prénom *',
            'sexe': 'Sexe *',
            'date_naissance': 'Date de naissance',
            'lieu_naissance': 'Lieu de naissance',
            'adresse': 'Adresse',
            'telephone': 'Téléphone *',
            'email': 'Email *',
            'specialite': 'Spécialité',
            'diplome': 'Diplôme',
            'date_recrutement': 'Date de recrutement *',
            'statut': 'Statut *',
            'photo': 'Photo de profil',
            'matieres': 'Matières enseignées',
        }