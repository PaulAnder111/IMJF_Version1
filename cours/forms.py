# cours/forms.py
from django import forms
from .models import Cours
from django.core.exceptions import ValidationError

class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['matiere', 'classe', 'enseignant', 'jour', 'heure_debut', 'heure_fin', 'salle', 'statut']
        widgets = {
            'jour': forms.Select(attrs={'class': 'form-select'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'salle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Salle B3'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        heure_debut = cleaned_data.get("heure_debut")
        heure_fin = cleaned_data.get("heure_fin")
        classe = cleaned_data.get("classe")
        enseignant = cleaned_data.get("enseignant")
        jour = cleaned_data.get("jour")

        # 1️⃣ Vérifie si heure_debut < heure_fin
        if heure_debut and heure_fin and heure_debut >= heure_fin:
            raise ValidationError("L'heure de début doit être avant l'heure de fin.")

        # 2️⃣ Vérifie conflits d'horaire pour la classe
        if Cours.objects.filter(classe=classe, jour=jour, heure_debut=heure_debut).exists():
            raise ValidationError(f"La classe {classe} a déjà un cours à cette heure.")

        # 3️⃣ Vérifie conflits d'horaire pour l’enseignant
        if Cours.objects.filter(enseignant=enseignant, jour=jour, heure_debut=heure_debut).exists():
            raise ValidationError(f"L'enseignant {enseignant} a déjà un cours à cette heure.")

        return cleaned_data


class CoursSearchForm(forms.Form):
    matiere = forms.ModelChoiceField(
        queryset=None, required=False, label="Matière"
    )
    classe = forms.ModelChoiceField(
        queryset=None, required=False, label="Classe"
    )
    enseignant = forms.ModelChoiceField(
        queryset=None, required=False, label="Enseignant"
    )
    jour = forms.ChoiceField(
        choices=[('', '--- Tous les jours ---')] + Cours.JOURS,
        required=False, label="Jour"
    )

    def __init__(self, *args, **kwargs):
        from matieres.models import Matiere
        from classes.models import Classe
        from enseignants.models import Enseignant

        super().__init__(*args, **kwargs)
        self.fields['matiere'].queryset = Matiere.objects.all()
        self.fields['classe'].queryset = Classe.objects.all()
        self.fields['enseignant'].queryset = Enseignant.objects.all()
