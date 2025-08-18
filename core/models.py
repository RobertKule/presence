from django.db import models
from django.contrib.auth.models import User

class Classe(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


class Etudiant(models.Model):
    matricule = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name="etudiants")

    def __str__(self):
        return f"{self.nom} {self.prenom or ''} ({self.matricule})"


class Cours(models.Model):
    nom = models.CharField(max_length=100)
    enseignant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cours")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name="cours")
    
    def __str__(self):
        return f"{self.nom} - {self.classe}"


class Seance(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="seances")
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField(blank=True, null=True)
    description=models.CharField(max_length=250,null=True,blank=True)

    def __str__(self):
        return f"{self.cours.nom} ({self.date} - {self.heure_debut})"


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
        unique_together = ("etudiant", "seance")

    def __str__(self):
        return f"{self.etudiant} - {self.seance} : {self.statut}"
