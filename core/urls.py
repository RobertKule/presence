# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # --- Authentification ---
    path('', views.dashboard, name="dashboard"),
    path('signup/', views.signup_view, name="signup"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),

    # --- Cours (enseignant) ---
    path('cours/', views.cours_list, name="cours_list"),
    path('cours/ajouter/', views.cours_create, name="cours_create"),
    path('cours/<int:pk>/modifier/', views.cours_update, name="cours_update"),
    path('cours/<int:pk>/supprimer/', views.cours_delete, name="cours_delete"),

    # --- Séances (enseignant) ---
    path('seances/', views.seance_list, name="seance_list"),
    path('seances/ajouter/', views.seance_create, name="seance_create"),
    path('seances/<int:pk>/modifier/', views.seance_update, name="seance_update"),
    path('seances/<int:pk>/supprimer/', views.seance_delete, name="seance_delete"),
    path('seances/<int:seance_id>/appel/', views.appel_presence, name="appel_presence"),

    # --- Statistiques & Export ---
    path('statistiques/', views.statistiques, name="statistiques"),
    path('export/<int:cours_id>/', views.export_excel, name="export_excel"),
    path('statistiques/<int:cours_id>/pdf/', views.export_pdf_statistiques, name="export_pdf_statistiques"),

    # --- Admin Dashboard ---
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # --- CRUD Enseignants ---
    path("admin/enseignant/add/", views.enseignant_create, name="enseignant_create"),
    path("admin/enseignant/<int:pk>/edit/", views.enseignant_update, name="enseignant_update"),
    path("admin/enseignant/<int:pk>/delete/", views.enseignant_delete, name="enseignant_delete"),

    # --- CRUD Classes ---
    path("admin/classe/add/", views.classe_create, name="classe_create"),
    path("admin/classe/<int:pk>/edit/", views.classe_update, name="classe_update"),
    path("admin/classe/<int:pk>/delete/", views.classe_delete, name="classe_delete"),

    # --- CRUD Étudiants ---
    path("admin/etudiant/add/", views.etudiant_create, name="etudiant_create"),
    path("admin/etudiant/<int:pk>/edit/", views.etudiant_update, name="etudiant_update"),
    path("admin/etudiant/<int:pk>/delete/", views.etudiant_delete, name="etudiant_delete"),

    # --- CRUD Cours (admin) ---
    path("admin/cours/add/", views.cours_create, name="cours_create"),
    path("admin/cours/<int:pk>/edit/", views.cours_update, name="cours_update"),
    path("admin/cours/<int:pk>/delete/", views.cours_delete, name="cours_delete"),
]
