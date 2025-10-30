# matieres/forms.py

from django import forms
from .models import Matiere

class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = ['code_matiere', 'nom_matiere', 'heure_hebdomadaire', 'statut']
        widgets = {
            'statut': forms.Select(),
        }