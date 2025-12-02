# annee_scolaire/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import AnneeScolaire

class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = ['nom', 'date_debut', 'date_fin', 'est_annee_courante', 'est_active']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900',
                'placeholder': 'Ex: 2024-2025'
            }),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900'
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900'
            }),
            'est_annee_courante': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
            'est_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-green-600 focus:ring-green-500'
            }),
        }
        labels = {
            'nom': "Nom de l'année scolaire",
            'date_debut': "Date de début",
            'date_fin': "Date de fin", 
            'est_annee_courante': "Définir comme année courante",
            'est_active': "Année active",
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        # Valide ke dat fen apye dat kòmansman
        if date_debut and date_fin and date_fin <= date_debut:
            raise ValidationError("La date de fin doit être après la date de début.")
        
        # Valide ke ane a pa fini nan pas
        if date_fin and date_fin < timezone.now().date():
            if cleaned_data.get('est_annee_courante'):
                raise ValidationError("Une année terminée ne peut pas être définie comme année courante.")
        
        return cleaned_data
    
    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if nom and AnneeScolaire.objects.filter(nom=nom).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Une année scolaire avec ce nom existe déjà.")
        return nom