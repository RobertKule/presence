# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.template.loader import render_to_string

import json
import openpyxl
from xhtml2pdf import pisa
from django.core.serializers.json import DjangoJSONEncoder

# Import des formulaires
from .forms import (
    SignUpForm, CoursForm, SeanceForm,
    EnseignantForm, ClasseForm, EtudiantForm
)

# Import des modèles
from .models import (
    Cours, Seance, Classe, User,
    Presence, Etudiant
)


# -------------------
# AUTHENTIFICATION
# -------------------

# Inscription
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login après inscription
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, "core/signup.html", {"form": form})


# Connexion
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, "core/login.html", {"form": form})


# Déconnexion
def logout_view(request):
    logout(request)
    return redirect('login')


# -------------------
# DASHBOARDS
# -------------------

# Dashboard enseignant
@login_required
def dashboard(request):
    cours = request.user.cours.all()  # uniquement les cours de l’utilisateur
    return render(request, "core/dashboard.html", {"cours": cours})


# Vérification si l’utilisateur est admin
def admin_required(user):
    return user.is_authenticated and user.role == "admin"


# Dashboard admin
@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):
    enseignants = User.objects.filter(role="enseignant")
    classes = Classe.objects.all()
    etudiants = Etudiant.objects.all()
    cours = Cours.objects.all()
    return render(request, "core/admin_dashboard.html", {
        "enseignants": enseignants,
        "classes": classes,
        "etudiants": etudiants,
        "cours": cours,
    })


# -------------------
# COURS (enseignant)
# -------------------

@login_required
def cours_list(request):
    cours = request.user.cours.all()
    return render(request, "core/cours_list.html", {"cours": cours})


@login_required
def cours_create(request):
    if request.method == "POST":
        form = CoursForm(request.POST)
        if form.is_valid():
            cours = form.save(commit=False)
            cours.enseignant = request.user
            cours.save()
            return redirect("cours_list")
    else:
        form = CoursForm()
    return render(request, "core/cours_form.html", {"form": form})


@login_required
def cours_update(request, pk):
    cours = get_object_or_404(Cours, pk=pk, enseignant=request.user)
    if request.method == "POST":
        form = CoursForm(request.POST, instance=cours)
        if form.is_valid():
            form.save()
            return redirect("cours_list")
    else:
        form = CoursForm(instance=cours)
    return render(request, "core/cours_form.html", {"form": form})


@login_required
def cours_delete(request, pk):
    cours = get_object_or_404(Cours, pk=pk, enseignant=request.user)
    if request.method == "POST":
        cours.delete()
        return redirect("cours_list")
    return render(request, "core/cours_confirm_delete.html", {"cours": cours})


# -------------------
# SEANCES
# -------------------

@login_required
def seance_list(request):
    seances = Seance.objects.filter(cours__enseignant=request.user)
    return render(request, "core/seance_list.html", {"seances": seances})


@login_required
def seance_create(request):
    if request.method == "POST":
        form = SeanceForm(request.POST)
        form.fields['cours'].queryset = Cours.objects.filter(enseignant=request.user)
        if form.is_valid():
            form.save()
            return redirect("seance_list")
    else:
        form = SeanceForm()
        form.fields['cours'].queryset = Cours.objects.filter(enseignant=request.user)
    return render(request, "core/seance_form.html", {"form": form})


@login_required
def seance_update(request, pk):
    seance = get_object_or_404(Seance, pk=pk, cours__enseignant=request.user)
    if request.method == "POST":
        form = SeanceForm(request.POST, instance=seance)
        form.fields['cours'].queryset = Cours.objects.filter(enseignant=request.user)
        if form.is_valid():
            form.save()
            return redirect("seance_list")
    else:
        form = SeanceForm(instance=seance)
        form.fields['cours'].queryset = Cours.objects.filter(enseignant=request.user)
    return render(request, "core/seance_form.html", {"form": form})


@login_required
def seance_delete(request, pk):
    seance = get_object_or_404(Seance, pk=pk, cours__enseignant=request.user)
    if request.method == "POST":
        seance.delete()
        return redirect("seance_list")
    return render(request, "core/seance_confirm_delete.html", {"seance": seance})


# -------------------
# PRESENCES
# -------------------

@login_required
def appel_presence(request, seance_id):
    seance = get_object_or_404(Seance, pk=seance_id, cours__enseignant=request.user)
    etudiants = Etudiant.objects.filter(classe=seance.cours.classe)

    if request.method == "POST":
        for etu in etudiants:
            statut = request.POST.get(f"statut_{etu.id}", "absent")
            Presence.objects.update_or_create(
                etudiant=etu,
                seance=seance,
                defaults={"statut": statut}
            )
        return redirect("seance_list")

    presences = {p.etudiant.id: p.statut for p in Presence.objects.filter(seance=seance)}
    return render(request, "core/appel_presence.html", {
        "seance": seance,
        "etudiants": etudiants,
        "presences": presences
    })


# -------------------
# STATISTIQUES
# -------------------

@login_required
def statistiques(request):
    cours_list = request.user.cours.all()
    stats_globales = []

    for cours in cours_list:
        total_seances = cours.seances.count()
        etudiants = cours.classe.etudiants.all()

        total_present = total_absent = total_retard = total_motif = 0
        etudiants_stats = []

        for etu in etudiants:
            present = etu.presences.filter(seance__cours=cours, statut="present").count()
            absent = etu.presences.filter(seance__cours=cours, statut="absent").count()
            retard = etu.presences.filter(seance__cours=cours, statut="retard").count()
            motif = etu.presences.filter(seance__cours=cours, statut="motif").count()

            total_present += present
            total_absent += absent
            total_retard += retard
            total_motif += motif

            etudiants_stats.append({
                "etudiant": f"{etu.nom} {etu.prenom or ''}",
                "present": present,
                "absent": absent,
                "retard": retard,
                "motif": motif,
            })

        stats_globales.append({
            "cours": cours.nom,
            "classe": cours.classe.nom,
            "total_seances": total_seances,
            "global": {
                "present": total_present,
                "absent": total_absent,
                "retard": total_retard,
                "motif": total_motif,
            },
            "etudiants_stats": etudiants_stats
        })

    return render(request, "core/statistiques.html", {
        "stats": stats_globales,
        "stats_json": json.dumps(stats_globales, cls=DjangoJSONEncoder)
    })


@login_required
def export_excel(request, cours_id):
    cours = get_object_or_404(Cours, id=cours_id, enseignant=request.user)
    etudiants = cours.classe.etudiants.all()
    seances = cours.seances.all().order_by("date")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Présences"

    # En-têtes
    headers = ["Étudiant"] + [str(s.date) for s in seances]
    ws.append(headers)

    # Lignes des étudiants
    for etu in etudiants:
        row = [f"{etu.nom} {etu.prenom}"]
        for s in seances:
            presence = Presence.objects.filter(etudiant=etu, seance=s).first()
            row.append(presence.statut if presence else "-")
        ws.append(row)

    # Export HTTP
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f'attachment; filename="presences_{cours.nom}.xlsx"'
    wb.save(response)
    return response


@login_required
def export_pdf_statistiques(request, cours_id):
    cours = get_object_or_404(Cours, id=cours_id, enseignant=request.user)
    etudiants = cours.classe.etudiants.all()
    seances = cours.seances.all().order_by("date")

    etudiants_stats = []
    total_present = total_absent = total_retard = total_motif = 0

    for etu in etudiants:
        present = etu.presences.filter(seance__cours=cours, statut="present").count()
        absent = etu.presences.filter(seance__cours=cours, statut="absent").count()
        retard = etu.presences.filter(seance__cours=cours, statut="retard").count()
        motif = etu.presences.filter(seance__cours=cours, statut="motif").count()

        total_present += present
        total_absent += absent
        total_retard += retard
        total_motif += motif

        etudiants_stats.append({
            "etudiant": f"{etu.nom} {etu.prenom}",
            "present": present,
            "absent": absent,
            "retard": retard,
            "motif": motif,
        })

    stats = {
        "cours": cours,
        "total_seances": seances.count(),
        "global": {
            "present": total_present,
            "absent": total_absent,
            "retard": total_retard,
            "motif": total_motif,
        },
        "etudiants_stats": etudiants_stats
    }

    html_string = render_to_string("core/statistiques_pdf.html", {"stats": stats})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="statistiques_{cours.nom}.pdf"'

    pisa_status = pisa.CreatePDF(src=html_string, dest=response)
    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF")

    return response


# -------------------
# ADMIN CRUD (enseignants, classes, étudiants, cours)
# -------------------

# --- ENSEIGNANTS ---
@login_required
@user_passes_test(admin_required)
def enseignant_create(request):
    if request.method == "POST":
        form = EnseignantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Enseignant ajouté avec succès")
            return redirect("admin_dashboard")
    else:
        form = EnseignantForm()
    return render(request, "core/admin_form.html", {"form": form, "title": "Ajouter Enseignant"})


@login_required
@user_passes_test(admin_required)
def enseignant_update(request, pk):
    enseignant = get_object_or_404(User, pk=pk, role="enseignant")
    if request.method == "POST":
        form = EnseignantForm(request.POST, instance=enseignant)
        if form.is_valid():
            form.save()
            messages.success(request, "Enseignant modifié avec succès")
            return redirect("admin_dashboard")
    else:
        form = EnseignantForm(instance=enseignant)
    return render(request, "core/admin_form.html", {"form": form, "title": "Modifier Enseignant"})


@login_required
@user_passes_test(admin_required)
def enseignant_delete(request, pk):
    enseignant = get_object_or_404(User, pk=pk, role="enseignant")
    enseignant.delete()
    messages.success(request, "Enseignant supprimé avec succès")
    return redirect("admin_dashboard")


# --- CLASSES ---
@login_required
@user_passes_test(admin_required)
def classe_create(request):
    if request.method == "POST":
        form = ClasseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Classe ajoutée avec succès")
            return redirect("admin_dashboard")
    else:
        form = ClasseForm()
    return render(request, "core/admin_form.html", {"form": form, "title": "Ajouter Classe"})


@login_required
@user_passes_test(admin_required)
def classe_update(request, pk):
    classe = get_object_or_404(Classe, pk=pk)
    if request.method == "POST":
        form = ClasseForm(request.POST, instance=classe)
        if form.is_valid():
            form.save()
            messages.success(request, "Classe modifiée avec succès")
            return redirect("admin_dashboard")
    else:
        form = ClasseForm(instance=classe)
    return render(request, "core/admin_form.html", {"form": form, "title": "Modifier Classe"})


@login_required
@user_passes_test(admin_required)
def classe_delete(request, pk):
    classe = get_object_or_404(Classe, pk=pk)
    classe.delete()
    messages.success(request, "Classe supprimée avec succès")
    return redirect("admin_dashboard")


# --- ETUDIANTS ---
@login_required
@user_passes_test(admin_required)
def etudiant_create(request):
    if request.method == "POST":
        form = EtudiantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Étudiant ajouté avec succès")
            return redirect("admin_dashboard")
    else:
        form = EtudiantForm()
    return render(request, "core/admin_form.html", {"form": form, "title": "Ajouter Étudiant"})


@login_required
@user_passes_test(admin_required)
def etudiant_update(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    if request.method == "POST":
        form = EtudiantForm(request.POST, instance=etudiant)
        if form.is_valid():
            form.save()
            messages.success(request, "Étudiant modifié avec succès")
            return redirect("admin_dashboard")
    else:
        form = EtudiantForm(instance=etudiant)
    return render(request, "core/admin_form.html", {"form": form, "title": "Modifier Étudiant"})


@login_required
@user_passes_test(admin_required)
def etudiant_delete(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    etudiant.delete()
    messages.success(request, "Étudiant supprimé avec succès")
    return redirect("admin_dashboard")


# --- COURS (admin) ---
@login_required
@user_passes_test(admin_required)
def cours_create(request):
    if request.method == "POST":
        form = CoursForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cours ajouté avec succès")
            return redirect("admin_dashboard")
    else:
        form = CoursForm()
    return render(request, "core/admin_form.html", {"form": form, "title": "Ajouter Cours"})


@login_required
@user_passes_test(admin_required)
def cours_update(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    if request.method == "POST":
        form = CoursForm(request.POST, instance=cours)
        if form.is_valid():
            form.save()
            messages.success(request, "Cours modifié avec succès")
            return redirect("admin_dashboard")
    else:
        form = CoursForm(instance=cours)
    return render(request, "core/admin_form.html", {"form": form, "title": "Modifier Cours"})


@login_required
@user_passes_test(admin_required)
def cours_delete(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    cours.delete()
    messages.success(request, "Cours supprimé avec succès")
    return redirect("admin_dashboard")
