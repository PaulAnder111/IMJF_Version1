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
        # Limite les classes disponibles aux classes actives
        self.fields['classe_actuelle'].queryset = Classe.objects.filter(statut='actif')
        # Supprime l'option vide automatique pour le champ classe_actuelle (ModelChoiceField)
        if hasattr(self.fields['classe_actuelle'], 'empty_label'):
            self.fields['classe_actuelle'].empty_label = None

        # Pour le champ sexe (ChoiceField), retire toute option vide automatique
        if 'sexe' in self.fields:
            # Filtre les choices pour enlever l'éventuelle valeur vide
            self.fields['sexe'].choices = [c for c in self.fields['sexe'].choices if c[0] != '']
            # Assure que le champ est requis au niveau du formulaire
            self.fields['sexe'].required = True