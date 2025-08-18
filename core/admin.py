from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Classe, Etudiant, Cours, Seance, Presence

admin.site.register(Classe)
admin.site.register(Etudiant)
admin.site.register(Cours)
admin.site.register(Seance)
admin.site.register(Presence)
