# core/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import (
    Cours, Seance, Classe, Etudiant, User as CustomUser
)


# -------------------
# AUTHENTIFICATION
# -------------------

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User   # <-- User natif Django pour l'inscription
        fields = ['username', 'email', 'password1', 'password2']


# -------------------
# COURS & SEANCES (enseignant)
# -------------------

class CoursForm(forms.ModelForm):
    """Formulaire pour l’enseignant (enseignant affecté automatiquement)."""
    class Meta:
        model = Cours
        fields = ['nom', 'classe']


class SeanceForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = ['cours', 'date', 'heure_debut', 'heure_fin', 'description']


# -------------------
# ADMIN CRUD
# -------------------

class EnseignantForm(forms.ModelForm):
    """Formulaire de création/modification des enseignants (admin)."""
    class Meta:
        model = CustomUser  # ton modèle User personnalisé (avec role)
        fields = ["username", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "enseignant"
        user.set_password(self.cleaned_data["password"])  # hash du mot de passe
        if commit:
            user.save()
        return user


class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ["nom"]


class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ["nom", "prenom", "classe"]


class AdminCoursForm(forms.ModelForm):
    """Formulaire cours utilisé par l’admin (choix manuel de l’enseignant)."""
    class Meta:
        model = Cours
        fields = ["nom", "classe", "enseignant"]
