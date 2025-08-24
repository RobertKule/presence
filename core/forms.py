# core/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import FileExtensionValidator

from .models import (
    Cours, Seance, Classe, Etudiant, User,
    Presence, AnneeUniversitaire
)


# -------------------
# AUTHENTIFICATION
# -------------------

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse email'
        })
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmation du mot de passe'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur ou email'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )


# -------------------
# FORMULAIRES ENSEIGNANT
# -------------------

class CoursForm(forms.ModelForm):
    """Formulaire pour la création/modification de cours par l'enseignant"""
    
    class Meta:
        model = Cours
        fields = ['nom', 'classe', 'type_cours', 'description', 'credit', 'volume_horaire']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du cours'}),
            'classe': forms.Select(attrs={'class': 'form-control'}),
            'type_cours': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du cours'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'volume_horaire': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
        }
        labels = {
            'type_cours': 'Type de cours',
            'credit': 'Nombre de crédits',
            'volume_horaire': 'Volume horaire (heures)'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Restreindre les classes si l'utilisateur n'est pas admin
        if self.user and not self.user.is_admin():
            # Ici vous pourriez limiter aux classes où l'enseignant a déjà des cours
            # Pour l'instant, on laisse toutes les classes
            pass
    
    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if len(nom) < 3:
            raise ValidationError("Le nom du cours doit contenir au moins 3 caractères.")
        return nom


class SeanceForm(forms.ModelForm):
    """Formulaire pour la création/modification de séances"""
    
    class Meta:
        model = Seance
        fields = ['cours', 'date', 'heure_debut', 'heure_fin', 'salle', 'description']
        widgets = {
            'cours': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'heure_debut': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'heure_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'salle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Salle de cours'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description de la séance'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Filtrer les cours pour n'afficher que ceux de l'enseignant
            self.fields['cours'].queryset = Cours.objects.filter(enseignant=self.user)
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        heure_debut = cleaned_data.get('heure_debut')
        heure_fin = cleaned_data.get('heure_fin')
        
        # Vérifier que la date n'est pas dans le passé
        if date and date < timezone.now().date():
            raise ValidationError("La date ne peut pas être dans le passé.")
        
        # Vérifier que l'heure de fin est après l'heure de début
        if heure_debut and heure_fin and heure_fin <= heure_debut:
            raise ValidationError("L'heure de fin doit être après l'heure de début.")
        
        return cleaned_data


class PresenceForm(forms.ModelForm):
    """Formulaire pour la gestion des présences"""
    
    class Meta:
        model = Presence
        fields = ['statut', 'heure_arrivee', 'motif_absence', 'notes']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'heure_arrivee': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'motif_absence': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Motif de l\'absence'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes supplémentaires'}),
        }


# -------------------
# FORMULAIRES ADMIN CRUD
# -------------------

class EnseignantForm(forms.ModelForm):
    """Formulaire de création/modification des enseignants (admin)"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Laissez vide pour ne pas modifier le mot de passe"
    )
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Confirmation du mot de passe"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'telephone', 'date_naissance', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active'].initial = True
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password != password_confirm:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'enseignant'
        
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        return user


class ClasseForm(forms.ModelForm):
    """Formulaire pour la création/modification des classes"""
    
    class Meta:
        model = Classe
        fields = ['nom', 'niveau', 'capacite_max', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau': forms.Select(attrs={'class': 'form-control'}),
            'capacite_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if Classe.objects.filter(nom=nom).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Une classe avec ce nom existe déjà.")
        return nom


class EtudiantForm(forms.ModelForm):
    """Formulaire pour la création/modification des étudiants"""
    
    class Meta:
        model = Etudiant
        fields = ['matricule', 'nom', 'prenom', 'sexe', 'date_naissance', 'email', 'telephone', 'classe']
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'classe': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_matricule(self):
        matricule = self.cleaned_data.get('matricule')
        if Etudiant.objects.filter(matricule=matricule).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Un étudiant avec ce matricule existe déjà.")
        return matricule
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Etudiant.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Un étudiant avec cet email existe déjà.")
        return email


class AdminCoursForm(forms.ModelForm):
    """Formulaire cours utilisé par l'admin (choix manuel de l'enseignant)"""
    
    class Meta:
        model = Cours
        fields = ['nom', 'code', 'enseignant', 'classe', 'type_cours', 'description', 'credit', 'volume_horaire', 'is_actif']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'enseignant': forms.Select(attrs={'class': 'form-control'}),
            'classe': forms.Select(attrs={'class': 'form-control'}),
            'type_cours': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'credit': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'volume_horaire': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'is_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['enseignant'].queryset = User.objects.filter(role='enseignant', is_active=True)
        self.fields['is_actif'].initial = True


# -------------------
# FORMULAIRES IMPORT/EXPORT
# -------------------

class ImportEtudiantsForm(forms.Form):
    """Formulaire pour l'import d'étudiants"""
    
    MODE_CHOICES = [
        ('create', 'Créer seulement les nouveaux'),
        ('update', 'Mettre à jour les existants et créer les nouveaux'),
    ]
    
    fichier = forms.FileField(
        label="Fichier des étudiants",
        help_text="Formats acceptés: CSV ou Excel (.xlsx). Colonnes: Matricule, Nom, Prénom, Email, Téléphone, Sexe, Date_naissance",
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx'])]
    )
    
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Classe"
    )
    
    mode = forms.ChoiceField(
        choices=MODE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='create',
        label="Mode d'import"
    )
    
    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        if fichier:
            if fichier.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("Le fichier ne doit pas dépasser 5MB.")
        return fichier


class ExportForm(forms.Form):
    """Formulaire pour l'export de données"""
    
    FORMAT_CHOICES = [
        ('excel', 'Excel (.xlsx)'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
    ]
    
    cours = forms.ModelChoiceField(
        queryset=Cours.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Cours"
    )
    
    date_debut = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=False,
        label="Date de début"
    )
    
    date_fin = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=False,
        label="Date de fin"
    )
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='excel',
        label="Format"
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            if self.user.is_admin():
                self.fields['cours'].queryset = Cours.objects.all()
            else:
                self.fields['cours'].queryset = Cours.objects.filter(enseignant=self.user)
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        if date_debut and date_fin and date_debut > date_fin:
            raise ValidationError("La date de début doit être avant la date de fin.")
        
        return cleaned_data


# -------------------
# FORMULAIRES DE RECHERCHE
# -------------------

class RechercheEtudiantForm(forms.Form):
    """Formulaire de recherche d'étudiants"""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom, prénom ou matricule...'
        }),
        label="Recherche"
    )
    
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Classe"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classe'].empty_label = "Toutes les classes"


class RechercheCoursForm(forms.Form):
    """Formulaire de recherche de cours"""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom de cours...'
        }),
        label="Recherche"
    )
    
    enseignant = forms.ModelChoiceField(
        queryset=User.objects.filter(role='enseignant'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Enseignant"
    )
    
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Classe"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['enseignant'].empty_label = "Tous les enseignants"
        self.fields['classe'].empty_label = "Toutes les classes"


class RechercheSeanceForm(forms.Form):
    """Formulaire de recherche de séances"""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par cours ou description...'
        }),
        label="Recherche"
    )
    
    date_debut = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=False,
        label="Date de début"
    )
    
    date_fin = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=False,
        label="Date de fin"
    )
    
    cours = forms.ModelChoiceField(
        queryset=Cours.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Cours"
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            if self.user.is_admin():
                self.fields['cours'].queryset = Cours.objects.all()
            else:
                self.fields['cours'].queryset = Cours.objects.filter(enseignant=self.user)
        
        self.fields['cours'].empty_label = "Tous les cours"
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        if date_debut and date_fin and date_debut > date_fin:
            raise ValidationError("La date de début doit être avant la date de fin.")
        
        return cleaned_data


# -------------------
# FORMULAIRES AVANCÉS
# -------------------

class AnneeUniversitaireForm(forms.ModelForm):
    """Formulaire pour la gestion des années universitaires"""
    
    class Meta:
        model = AnneeUniversitaire
        fields = ['nom', 'date_debut', 'date_fin', 'is_active']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        if date_debut and date_fin and date_debut >= date_fin:
            raise ValidationError("La date de fin doit être après la date de début.")
        
        return cleaned_data


class AbsenceJustifieeForm(forms.ModelForm):
    """Formulaire pour la gestion des absences justifiées"""
    
    class Meta:
        model = Presence
        fields = ['motif_absence', 'justificatif', 'notes']
        widgets = {
            'motif_absence': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Détaillez le motif de l\'absence...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes supplémentaires...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['justificatif'].required = True