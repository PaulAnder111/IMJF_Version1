# cours/forms.py

from django import forms
from .models import Cours

class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = [
            'matiere', 'classe', 'enseignant',
            'jour', 'heure_debut', 'heure_fin', 'salle', 'statut'
        ]
        widgets = {
            'heure_debut': forms.TimeInput(attrs={'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time'}),
        }