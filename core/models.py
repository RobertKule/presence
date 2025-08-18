# core/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser


# -------------------
# UTILISATEUR
# -------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('enseignant', 'Enseignant'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='enseignant')

    def is_admin(self):
        """Vérifie si l’utilisateur est un administrateur."""
        return self.role == 'admin'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# -------------------
# CLASSE
# -------------------
class Classe(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


# -------------------
# ETUDIANT
# -------------------
class Etudiant(models.Model):
    matricule = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name="etudiants")

    def __str__(self):
        return f"{self.nom} {self.prenom or ''} ({self.matricule})"


# -------------------
# COURS
# -------------------
class Cours(models.Model):
    nom = models.CharField(max_length=100)
    enseignant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cours")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name="cours")
    
    def __str__(self):
        return f"{self.nom} - {self.classe}"


# -------------------
# SEANCE
# -------------------
class Seance(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="seances")
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField(blank=True, null=True)
    description = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return f"{self.cours.nom} ({self.date} - {self.heure_debut})"


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
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="presences")
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE, related_name="presences")
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default="absent")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["etudiant", "seance"], name="unique_presence")
        ]

    def __str__(self):
        return f"{self.etudiant} - {self.seance} : {self.get_statut_display()}"
