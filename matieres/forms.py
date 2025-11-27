# matieres/forms.py

from django import forms
from .models import Matiere

class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = ['nom_matiere', 'heure_hebdomadaire', 'statut']  # code_matiere retire, li otomatik
        widgets = {
            'statut': forms.Select(),
        }