# inscriptions/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Inscription
from classes.models import Classe
import re
from core.validators import validate_phone_prefix, validate_unique_across_models, format_phone_international

class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = [
            'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe', 'adresse', 'niveau',
            'classe', 'annee_scolaire',
            'personne_responsable', 'profession_responsable', 'telephone_responsable', 'email_responsable',
            'ecole_origine',
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 3}),
            'annee_scolaire': forms.TextInput(attrs={'placeholder': 'Ex: 2025-2026'}),
            'classe': forms.Select(),
            'sexe': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ajoute klas CSS pou tout chan
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

        # filtre klas aktif yo sèlman
        self.fields['classe'].queryset = Classe.objects.filter(statut='actif')

        # placeholders itil
        self.fields['nom'].widget.attrs.update({'placeholder': "Nom de famille"})
        self.fields['prenom'].widget.attrs.update({'placeholder': "Prénom de l'élève", 'autofocus': True})

    def clean(self):
        cleaned_data = super().clean()
        telephone = cleaned_data.get('telephone_responsable')
        email = cleaned_data.get('email_responsable')
        # Validate phone prefix and uniqueness across the system
        if telephone:
            try:
                validate_phone_prefix(telephone)
                validate_unique_across_models('telephone', telephone, instance=self.instance)
            except ValidationError as ve:
                self.add_error('telephone_responsable', ve)
            else:
                # Format the telephone for storage
                cleaned_data['telephone_responsable'] = format_phone_international(telephone)

        if email:
            try:
                validate_unique_across_models('email', email, instance=self.instance)
            except ValidationError as ve:
                self.add_error('email_responsable', ve)
        return cleaned_data

    def clean_annee_scolaire(self):
        annee = self.cleaned_data.get('annee_scolaire')
        if not re.match(r'^\d{4}-\d{4}$', annee):
            raise ValidationError("Le format de l'année scolaire doit être : 2025-2026")
        return annee
