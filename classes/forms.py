from django import forms
from .models import Classe

class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ['nom_classe', 'code_classe', 'niveau', 'capacite_max', 'statut']
        widgets = {
            'nom_classe': forms.TextInput(attrs={'class': 'form-control'}),
            'code_classe': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau': forms.Select(attrs={'class': 'form-control'}),
            'capacite_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nom_classe': "Nom de la classe",
            'code_classe': "Code Classe",
            'niveau': "Niveau scolaire",
            'capacite_max': "Capacité maximale",
            'statut': "Statut",
        }