from django import forms
from .models import Eleve
from classes.models import Classe

class EleveForm(forms.ModelForm):
    class Meta:
        model = Eleve
        fields = [
            'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe', 'adresse', 'niveau',
            'classe_actuelle', 'statut', 'photo','statut'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nom': "Nom de l'élève",
            'prenom': "Prénom de l'élève",
            'date_naissance': "Date de naissance",
            'lieu_naissance': "Lieu de naissance",
            'sexe': "Sexe",
            'adresse': "Adresse complète",
            'niveau': "Niveau scolaire",
            'classe_actuelle': "Classe actuelle",
            'statut': "Statut",
            'photo': "Photo de l'élève (optionnel)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classe_actuelle'].queryset = Classe.objects.filter(statut='actif')