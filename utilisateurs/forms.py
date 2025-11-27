
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from core.validators import validate_phone_prefix, validate_unique_across_models, format_phone_international

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'role', 'photo']

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            validate_phone_prefix(telephone)
            validate_unique_across_models('telephone', telephone, instance=None)
            # Format for storage
            return format_phone_international(telephone)
        return telephone

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'role', 'photo', 'is_active']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id  # ID itilizatè ou ap modifye a
        if CustomUser.objects.exclude(id=user_id).filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre utilisateur.")
        # check email uniqueness across other configured models
        validate_unique_across_models('email', email, instance=self.instance)
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        user_id = self.instance.id
        if telephone:
            # first ensure the operator prefix is allowed
            validate_phone_prefix(telephone)
            # check uniqueness across the system
            validate_unique_across_models('telephone', telephone, instance=self.instance)
            # Format to canonical international form
            return format_phone_international(telephone)
        return telephone
