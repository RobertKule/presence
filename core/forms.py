from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Cours,Seance

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['nom', 'classe']  # pas "enseignant" car on l’associera automatiquement

class SeanceForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = ['cours', 'date', 'heure_debut', 'heure_fin', 'description']
