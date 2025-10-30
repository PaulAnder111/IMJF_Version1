from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )

# Fòm pou kreye yon itilizatè
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'role', 'photo', 'password1', 'password2']

# Fòm pou modifye yon itilizatè (update)
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'role', 'photo', 'is_active']

    # Validation pou imèl pou evite doublon
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Cet email est déjà utilisé.")
        return email
