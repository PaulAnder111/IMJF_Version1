# cours/forms.py
from django import forms
from .models import Cours
from matieres.models import Matiere
from classes.models import Classe
from enseignants.models import Enseignant

class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['matiere', 'classe', 'enseignant', 'jour', 'statut', 'heure_debut', 'heure_fin', 'salle']
        widgets = {
            'salle': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-yellow-500 focus:border-transparent'}),
        }

    jour = forms.ChoiceField(
        choices=Cours.JOURS,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-yellow-500 focus:border-transparent'})
    )
    statut = forms.ChoiceField(
        choices=Cours.STATUTS_COURS,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-yellow-500 focus:border-transparent'})
    )
    heure_debut = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-yellow-500 focus:border-transparent', 'type': 'time'})
    )
    heure_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-yellow-500 focus:border-transparent', 'type': 'time'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Peuple donnen yo
        self.fields['matiere'].queryset = Matiere.objects.all()
        self.fields['classe'].queryset = Classe.objects.all()
        self.fields['enseignant'].queryset = Enseignant.objects.all()
        # Mete klas pou seleksyon
        for field in ['matiere', 'classe', 'enseignant']:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-yellow-500 focus:border-transparent'
            })