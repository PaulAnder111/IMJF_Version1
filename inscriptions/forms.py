# inscriptions/forms.py
from django import forms
from .models import Inscription
from classes.models import Classe

class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = [
            # Enfòmasyon eleve a
            'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe', 'adresse', 'niveau',
            # Enfòmasyon akademik
            'classe', 'annee_scolaire',
            # Enfòmasyon paran/titilè
            'personne_responsable', 'profession_responsable', 'telephone_responsable', 'email_responsable',
            # Opsyonèl
            'ecole_origine',
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'annee_scolaire': forms.TextInput(attrs={'placeholder': 'Ex: 2025-2026', 'class': 'form-control'}),
            'classe': forms.Select(attrs={'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nom': "Nom de l'élève",
            'prenom': "Prénom de l'élève",
            'date_naissance': "Date de naissance",
            'lieu_naissance': "Lieu de naissance",
            'sexe': "Sexe",
            'adresse': "Adresse complète (rue, commune, département)",
            'niveau': "Niveau scolaire",
            'classe': "Classe choisie",
            'annee_scolaire': "Année scolaire",
            'personne_responsable': "Nom du responsable légal",
            'profession_responsable': "Profession du responsable",
            'telephone_responsable': "Téléphone du responsable",
            'email_responsable': "Email du responsable (optionnel)",
            'ecole_origine': "École d'origine (optionnel)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classe'].queryset = Classe.objects.filter(statut='actif')