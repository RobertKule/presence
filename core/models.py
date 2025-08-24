# core/models.py

import uuid
import time
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinLengthValidator, RegexValidator


# -------------------
# UTILISATEUR
# -------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('enseignant', 'Enseignant'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='enseignant',
        verbose_name="Rôle"
    )
    
    email = models.EmailField(
        unique=True,
        verbose_name="Adresse email"
    )
    
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone"
    )
    
    date_naissance = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date de naissance"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['username']

    def is_admin(self):
        return self.role == 'admin'

    def is_enseignant(self):
        return self.role == 'enseignant'

    def get_absolute_url(self):
        return reverse('enseignant_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


# -------------------
# CLASSE
# -------------------

# -------------------
# CLASSE
# -------------------
class Classe(models.Model):
    NIVEAU_CHOICES = [
        ('L0', 'Preparatoire'),
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
    ]
    
    nom = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Nom de la classe"
    )
    
    niveau = models.CharField(
        max_length=10,
        choices=NIVEAU_CHOICES,
        blank=True,
        null=True,
        verbose_name="Niveau"
    )
    
    capacite_max = models.PositiveIntegerField(
        default=30,
        verbose_name="Capacité maximale"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)  # Supprimez default=timezone.now
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ['niveau', 'nom']

    def __str__(self):
        if self.niveau:
            return f"{self.nom} ({self.get_niveau_display()})"
        return self.nom

    def get_absolute_url(self):
        return reverse('classe_detail', kwargs={'pk': self.pk})

    def etudiants_count(self):
        return self.etudiants.count()

    def cours_count(self):
        return self.cours.count()

    def is_pleine(self):
        return self.etudiants.count() >= self.capacite_max


# -------------------
# ETUDIANT
# -------------------
class Etudiant(models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    matricule = models.CharField(
        max_length=20, 
        unique=True,
        validators=[MinLengthValidator(5)],
        verbose_name="Matricule"
    )
    
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom"
    )
    
    prenom = models.CharField(
        max_length=100,
        verbose_name="Prénom"
    )
    
    sexe = models.CharField(
        max_length=1,
        choices=SEXE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Sexe"
    )
    
    date_naissance = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date de naissance"
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email"
    )
    
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone"
    )
    
    classe = models.ForeignKey(
        Classe, 
        on_delete=models.CASCADE, 
        related_name="etudiants",
        verbose_name="Classe"
    )
    
    photo = models.ImageField(
        upload_to='etudiants/',
        blank=True,
        null=True,
        verbose_name="Photo"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"
        ordering = ['classe', 'nom', 'prenom']
        indexes = [
            models.Index(fields=['matricule']),
            models.Index(fields=['nom', 'prenom']),
            models.Index(fields=['classe']),
        ]

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.matricule})"

    def get_absolute_url(self):
        return reverse('etudiant_detail', kwargs={'pk': self.pk})

    def get_full_name(self):
        return f"{self.nom} {self.prenom}"

    def age(self):
        if self.date_naissance:
            today = timezone.now().date()
            return today.year - self.date_naissance.year - (
                (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
            )
        return None

    def taux_presence_global(self):
        total_presences = self.presences.count()
        if total_presences == 0:
            return 0
        
        presentes = self.presences.filter(statut__in=['present', 'retard']).count()
        return (presentes / total_presences) * 100


# -------------------
# COURS
# -------------------
# -------------------
# COURS
# -------------------
class Cours(models.Model):
    TYPE_COURS_CHOICES = [
        ('cours', 'Cours'),
        ('td', 'Travaux Dirigés'),
        ('tp', 'Travaux Pratiques'),
        ('projet', 'Projet'),
    ]
    
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom du cours"
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,  
        null=True,   
        verbose_name="Code du cours"
    )
    
    enseignant = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="cours_enseignant",
        limit_choices_to={'role': 'enseignant'},
        verbose_name="Enseignant"
    )
    
    classe = models.ForeignKey(
        Classe, 
        on_delete=models.CASCADE, 
        related_name="cours",
        verbose_name="Classe"
    )
    
    type_cours = models.CharField(
        max_length=20,
        choices=TYPE_COURS_CHOICES,
        default='cours',
        verbose_name="Type de cours"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )
    
    credit = models.PositiveIntegerField(
        default=3,
        verbose_name="Crédits"
    )
    
    volume_horaire = models.PositiveIntegerField(
        default=30,
        verbose_name="Volume horaire (heures)"
    )
    
    is_actif = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            # Génération automatique du code
            base_nom = ''.join([c for c in self.nom if c.isalnum()]).upper()[:4]
            base_classe = self.classe.nom[:3].upper() if self.classe else 'GEN'
            timestamp = str(int(time.time()))[-3:]
            self.code = f"{base_nom}-{base_classe}-{timestamp}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['classe', 'nom']
        unique_together = ['nom', 'classe', 'enseignant']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['enseignant']),
            models.Index(fields=['classe']),
        ]

    def __str__(self):
        return f"{self.nom} - {self.classe.nom} ({self.code})"

    def get_absolute_url(self):
        return reverse('cours_detail', kwargs={'pk': self.pk})

    def seances_count(self):
        return self.seances.count()

    def etudiants_count(self):
        return self.classe.etudiants.count()

    def taux_presence_global(self):
        total_presences_attendues = self.seances_count() * self.etudiants_count()
        if total_presences_attendues == 0:
            return 0
        
        total_presences = Presence.objects.filter(
            seance__cours=self,
            statut__in=['present', 'retard']
        ).count()
        
        return (total_presences / total_presences_attendues) * 100


# -------------------
# SEANCE
# -------------------
class Seance(models.Model):
    cours = models.ForeignKey(
        Cours, 
        on_delete=models.CASCADE, 
        related_name="seances",
        verbose_name="Cours"
    )
    
    date = models.DateField(
        verbose_name="Date"
    )
    
    heure_debut = models.TimeField(
        verbose_name="Heure de début"
    )
    
    heure_fin = models.TimeField(
        verbose_name="Heure de fin"
    )
    
    salle = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Salle"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )
    
    is_annulee = models.BooleanField(
        default=False,
        verbose_name="Annulée"
    )
    
    motif_annulation = models.TextField(
        blank=True,
        null=True,
        verbose_name="Motif d'annulation"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Séance"
        verbose_name_plural = "Séances"
        ordering = ['-date', 'heure_debut']
        indexes = [
            models.Index(fields=['cours']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.cours.nom} - {self.date.strftime('%d/%m/%Y')} {self.heure_debut}"

    def get_absolute_url(self):
        return reverse('seance_detail', kwargs={'pk': self.pk})

    def duree(self):
        if self.heure_debut and self.heure_fin:
            debut_minutes = self.heure_debut.hour * 60 + self.heure_debut.minute
            fin_minutes = self.heure_fin.hour * 60 + self.heure_fin.minute
            return fin_minutes - debut_minutes
        return 0

    def presences_count(self):
        return self.presences.count()

    def presences_present(self):
        return self.presences.filter(statut__in=['present', 'retard']).count()

    def presences_absentes(self):
        return self.presences.filter(statut__in=['absent', 'motif']).count()

    def taux_presence(self):
        total_etudiants = self.cours.classe.etudiants.count()
        if total_etudiants == 0:
            return 0
        return (self.presences_present() / total_etudiants) * 100


# -------------------
# PRESENCE
# -------------------
class Presence(models.Model):
    STATUS_CHOICES = [
        ("present", "Présent"),
        ("retard", "En retard"),
        ("absent", "Absent"),
        ("motif", "Absent avec motif"),
    ]
    
    etudiant = models.ForeignKey(
        Etudiant, 
        on_delete=models.CASCADE, 
        related_name="presences",
        verbose_name="Étudiant"
    )
    
    seance = models.ForeignKey(
        Seance, 
        on_delete=models.CASCADE, 
        related_name="presences",
        verbose_name="Séance"
    )
    
    statut = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default="absent",
        verbose_name="Statut"
    )
    
    heure_arrivee = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Heure d'arrivée"
    )
    
    motif_absence = models.TextField(
        blank=True,
        null=True,
        verbose_name="Motif d'absence"
    )
    
    justificatif = models.FileField(
        upload_to='justificatifs/',
        blank=True,
        null=True,
        verbose_name="Justificatif"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        constraints = [
            models.UniqueConstraint(fields=["etudiant", "seance"], name="unique_presence")
        ]
        indexes = [
            models.Index(fields=['etudiant', 'seance']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"{self.etudiant} - {self.seance} : {self.get_statut_display()}"

    def get_absolute_url(self):
        return reverse('presence_detail', kwargs={'pk': self.pk})

    def is_present(self):
        return self.statut in ['present', 'retard']

    def save(self, *args, **kwargs):
        # Vérifier que l'étudiant appartient à la classe du cours
        if self.etudiant.classe != self.seance.cours.classe:
            raise ValueError("L'étudiant n'appartient pas à la classe de ce cours")
        
        super().save(*args, **kwargs)


# -------------------
# MODÈLES ADDITIONNELS (optionnels)
# -------------------

class AnneeUniversitaire(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Année universitaire"
        verbose_name_plural = "Années universitaires"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        # Désactiver les autres années si celle-ci est active
        if self.is_active:
            AnneeUniversitaire.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Semestre(models.Model):
    nom = models.CharField(max_length=50)
    annee_universitaire = models.ForeignKey(AnneeUniversitaire, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()

    class Meta:
        verbose_name = "Semestre"
        verbose_name_plural = "Semestres"
        unique_together = ['nom', 'annee_universitaire']

    def __str__(self):
        return f"{self.nom} - {self.annee_universitaire}"


class AbsenceJustifiee(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    motif = models.TextField()
    justificatif = models.FileField(upload_to='absences_justifiees/')
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ], default='en_attente')

    class Meta:
        verbose_name = "Absence justifiée"
        verbose_name_plural = "Absences justifiées"

    def __str__(self):
        return f"{self.etudiant} - {self.date_debut} au {self.date_fin}"
    
# -------------------
# ADMIN REGISTRATION
# -------------------

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Classe, Etudiant, Cours, Seance, Presence, User

# Admin personnalisé pour le modèle User
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'telephone', 'date_naissance')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'telephone', 'date_naissance')
        }),
    )
