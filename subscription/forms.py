from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
import re
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import CommonPasswordValidator
from django.core.exceptions import ValidationError as DjangoValidationError

# Formulaire personnalisé d'inscription
class CustomRegistrationForm(UserCreationForm):
    prenom = forms.CharField(max_length=30, required=True, help_text='Optional.')
    nom = forms.CharField(max_length=30, required=True, help_text='Optional.')

    class Meta:
        model = User
        fields = ['prenom', 'nom', 'username', 'email', 'password1', 'password2']
        labels = {
            'prenom': 'Prénom',  # Étiquette personnalisée pour le champ "prenom"
            'nom': 'Nom',  # Étiquette personnalisée pour le champ "nom"
            'username': 'Nom d\'utilisateur',  # Étiquette personnalisée pour le champ "username"
            'email': 'Adresse e-mail',  # Étiquette personnalisée pour le champ "email"
            'password1': 'Mot de passe',  # Étiquette personnalisée pour le champ "password1"
            'password2': 'Confirmation du mot de passe',  # Étiquette personnalisée pour le champ "password2"
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()

        # Créez automatiquement le profil utilisateur associé
        UserProfile.objects.create(user=user)

        return user

    def clean_prenom(self):
        prenom = self.cleaned_data['prenom']
        if not prenom.isalpha():
            raise forms.ValidationError("Le prénom ne doit contenir que des lettres.")
        return prenom

    def clean_nom(self):
        nom = self.cleaned_data['nom']
        if not nom.isalpha():
            raise forms.ValidationError("Le nom ne doit contenir que des lettres.")
        return nom
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Un utilisateur avec ce nom d'utilisateur existe déjà.")
        return username

    #def clean_email(self):
        #email = self.cleaned_data['email']
        #if User.objects.filter(email=email).exists():
            #raise forms.ValidationError("Un utilisateur avec cette adresse e-mail existe déjà.")
        #return email

    def clean_password1(self):
        password1 = self.cleaned_data['password1']

        if len(password1) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")

        common_validator = CommonPasswordValidator()
        try:
            common_validator.validate(password1, self)
        except DjangoValidationError as e:
            if 'password_too_common' in str(e):
                raise forms.ValidationError(
                    _("Votre mot de passe est trop courant."),
                    code='password_too_common',
                )

        if not any(char.isupper() for char in password1) and not any(
                char in "!@#$%^&*()-_=+[]{}|;:'\",.<>/? " for char in password1):
            raise forms.ValidationError(
                "Le mot de passe doit contenir au moins une lettre majuscule ou un caractère spécial.")

        return password1
    def clean_password2(self):

            password1 = self.cleaned_data.get('password1')
            password2 = self.cleaned_data.get('password2')

            if password1 and password2 and password1 != password2:
                raise forms.ValidationError("Les deux mots de passe ne sont pas identiques.")

            return password2