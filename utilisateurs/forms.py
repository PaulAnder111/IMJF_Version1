# utilisateurs/forms.py
from django import forms
from .models import CustomUser
from .forms import LoginForm, UserUpdateForm, CustomUserCreationForm
from core.models import BaseModel
from django.core.exceptions import ValidationError

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and BaseModel.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé dans le système.")
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone and BaseModel.objects.filter(telephone=telephone).exists():
            raise ValidationError("Ce numéro de téléphone est déjà utilisé dans le système.")
        return telephone
