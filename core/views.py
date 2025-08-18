from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CoursForm,SeanceForm
from .models import Cours,Seance

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

# Dashboard protégé
@login_required
def dashboard(request):
    cours = request.user.cours.all()  # uniquement ses cours
    return render(request, "core/dashboard.html", {"cours": cours})


# Liste des cours de l’enseignant
@login_required
def cours_list(request):
    cours = request.user.cours.all()
    return render(request, "core/cours_list.html", {"cours": cours})

# Ajouter un cours
@login_required
def cours_create(request):
    if request.method == "POST":
        form = CoursForm(request.POST)
        if form.is_valid():
            cours = form.save(commit=False)
            cours.enseignant = request.user  # lie le cours à l’enseignant connecté
            cours.save()
            return redirect("cours_list")
    else:
        form = CoursForm()
    return render(request, "core/cours_form.html", {"form": form})

# Modifier un cours
@login_required
def cours_update(request, pk):
    cours = get_object_or_404(Cours, pk=pk, enseignant=request.user)  # sécurité : appartient à l’enseignant
    if request.method == "POST":
        form = CoursForm(request.POST, instance=cours)
        if form.is_valid():
            form.save()
            return redirect("cours_list")
    else:
        form = CoursForm(instance=cours)
    return render(request, "core/cours_form.html", {"form": form})

# Supprimer un cours
@login_required
def cours_delete(request, pk):
    cours = get_object_or_404(Cours, pk=pk, enseignant=request.user)
    if request.method == "POST":
        cours.delete()
        return redirect("cours_list")
    return render(request, "core/cours_confirm_delete.html", {"cours": cours})


# Liste des séances (par enseignant)
@login_required
def seance_list(request):
    seances = Seance.objects.filter(cours__enseignant=request.user)
    return render(request, "core/seance_list.html", {"seances": seances})

# Créer une séance
@login_required
def seance_create(request):
    if request.method == "POST":
        form = SeanceForm(request.POST)
        # Limiter les cours au professeur connecté
        form.fields['cours'].queryset = Cours.objects.filter(enseignant=request.user)
        if form.is_valid():
            seance = form.save()
            return redirect("seance_list")
    else:
        form = SeanceForm()
        form.fields['cours'].queryset = Cours.objects.filter(enseignant=request.user)
    return render(request, "core/seance_form.html", {"form": form})

# Modifier une séance
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

# Supprimer une séance
@login_required
def seance_delete(request, pk):
    seance = get_object_or_404(Seance, pk=pk, cours__enseignant=request.user)
    if request.method == "POST":
        seance.delete()
        return redirect("seance_list")
    return render(request, "core/seance_confirm_delete.html", {"seance": seance})

from .models import Presence, Etudiant

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

    # Récupérer les présences déjà enregistrées
    presences = {p.etudiant.id: p.statut for p in Presence.objects.filter(seance=seance)}
    return render(request, "core/appel_presence.html", {
        "seance": seance,
        "etudiants": etudiants,
        "presences": presences
    })
from django.db.models import Count, Q
import openpyxl
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cours, Etudiant, Presence
import json
from django.core.serializers.json import DjangoJSONEncoder

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
    headers = ["Étudiant"]
    for s in seances:
        headers.append(str(s.date))
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

from django.template.loader import render_to_string
from django.http import HttpResponse
import tempfile
from weasyprint import HTML

@login_required
def export_pdf_statistiques(request, cours_id):
    # Vérifier que l'enseignant a accès au cours
    cours = get_object_or_404(Cours, id=cours_id, enseignant=request.user)
    etudiants = cours.classe.etudiants.all()
    seances = cours.seances.all().order_by("date")

    # Calcul stats
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

    # Render HTML
    html_string = render_to_string("core/statistiques_pdf.html", {"stats": stats})

    # Création PDF
    with tempfile.NamedTemporaryFile(delete=True) as output:
        HTML(string=html_string).write_pdf(target=output.name)
        output.seek(0)
        pdf = output.read()

    response = HttpResponse(pdf, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="statistiques_{cours.nom}.pdf"'
    return response



