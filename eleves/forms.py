from django import forms
from .models import Eleve
from classes.models import Classe
from annee_scolaire.models import AnneeScolaire  # Ajoute sa a

class EleveForm(forms.ModelForm):
    class Meta:
        model = Eleve
        fields = [
            'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe', 'adresse', 'niveau',
            'classe_actuelle', 'statut', 'photo', 'annee_scolaire'  # 👈 Chanje pou 'annee_scolaire' (singilye)
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-control'}),  # 👈 Ajoute sa a
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
            'annee_scolaire': "Année Scolaire",  # 👈 Chanje pou 'annee_scolaire'
            'statut': "Statut",
            'photo': "Photo de l'élève (optionnel)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limite les classes disponibles aux classes actives
        self.fields['classe_actuelle'].queryset = Classe.objects.filter(statut='actif')
        
        # 👈 AJOUTE: Limite annee_scolaire a annee actuelle oswa tout annee aktif
        self.fields['annee_scolaire'].queryset = AnneeScolaire.objects.filter(est_active=True)
        
        # Supprime l'option vide automatique pour le champ classe_actuelle
        if hasattr(self.fields['classe_actuelle'], 'empty_label'):
            self.fields['classe_actuelle'].empty_label = None

        # Pour le champ sexe
        if 'sexe' in self.fields:
            self.fields['sexe'].choices = [c for c in self.fields['sexe'].choices if c[0] != '']
            self.fields['sexe'].required = True

        # Pour le champ statut
        if 'statut' in self.fields:
            self.fields['statut'].choices = [c for c in self.fields['statut'].choices if c[0] != '']
            self.fields['statut'].required = True

        # Ajoute des classes CSS aux champs pour le style
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'
        
        # 👈 RETIRE: Tout bagay ki gen rapò ak 'annees_scolaires' (ManyToMany)
        # Pa gen CheckboxSelectMultiple ni lòt bagay pou annee_scolaire