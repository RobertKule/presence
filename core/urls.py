# core/urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # -------------------------------
    # AUTHENTIFICATION
    # -------------------------------
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup_view, name="signup"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    
    # -------------------------------
    # DASHBOARDS
    # -------------------------------
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path('synthese/', views.synthese_enseignant, name="synthese_enseignant"),

    # -------------------------------
    # GESTION DES COURS (ENSEIGNANT)
    # -------------------------------
    path('mes-cours/', views.mes_cours, name="mes_cours"),
    path('mes-cours/ajouter/', views.cours_create, name="cours_create"),
    path('mes-cours/<int:pk>/', views.cours_detail, name="cours_detail"),
    path('mes-cours/<int:pk>/modifier/', views.cours_update, name="cours_update"),
    path('mes-cours/<int:pk>/supprimer/', views.cours_delete, name="cours_delete"),

    # -------------------------------
    # GESTION DES SÉANCES
    # -------------------------------
    path('seances/', views.seance_list, name="seance_list"),
    path('seances/ajouter/', views.seance_create, name="seance_create"),
    path('seances/<int:pk>/modifier/', views.seance_update, name="seance_update"),
    path('seances/<int:pk>/supprimer/', views.seance_delete, name="seance_delete"),
    path('seances/<int:seance_id>/appel/', views.appel_presence, name="appel_presence"),
    # path('api/presence-rapide/', views.presence_rapide, name="presence_rapide"),

    # -------------------------------
    # GESTION DES ÉTUDIANTS
    # -------------------------------
    path('mes-etudiants/', views.mes_etudiants, name="mes_etudiants"),
    path('importer-etudiants/', views.importer_etudiants, name='importer_etudiants'),
    path('telecharger-modele-import/', views.telecharger_modele_import, name='telecharger_modele_import'),

    # -------------------------------
    # STATISTIQUES & EXPORT
    # -------------------------------
    path('statistiques/', views.statistiques, name="statistiques"),
    path('export/<int:cours_id>/excel/', views.export_excel, name="export_excel"),
    path('export/<int:cours_id>/pdf/', views.export_pdf_statistiques, name="export_pdf_statistiques"),

    # -------------------------------
    # API ENDPOINTS
    # -------------------------------
    path('api/stats/cours/<int:cours_id>/', views.api_stats_cours, name="api_stats_cours"),
    path('api/presences/seance/<int:seance_id>/', views.api_presences_seance, name="api_presences_seance"),
    path('api/recherche/etudiants/', views.api_recherche_etudiants, name="api_recherche_etudiants"),
    path('api/recherche/cours/', views.api_recherche_cours, name="api_recherche_cours"),
    
    path('seances/<int:seance_id>/ajouter-etudiant/', views.ajouter_etudiant_rapide, name="ajouter_etudiant_rapide"),
    path('api/stats/cours/<int:cours_id>/', views.api_stats_cours, name="api_stats_cours"),
    
    # -------------------------------
    # ADMIN CRUD - ENSEIGNANTS
    # -------------------------------
    path("admin_enseignants/", views.enseignant_list, name="enseignant_list"),
    path("admin_enseignants/ajouter/", views.enseignant_create, name="enseignant_create"),
    path("admin_enseignants/<int:pk>/modifier/", views.enseignant_update, name="enseignant_update"),
    path("admin_enseignants/<int:pk>/supprimer/", views.enseignant_delete, name="enseignant_delete"),

    # -------------------------------
    # ADMIN CRUD - CLASSES
    # -------------------------------
    path("admin_classes/", views.classe_list, name="classe_list"),
    path("admin_classes/ajouter/", views.classe_create, name="classe_create"),
    path("admin_classes/<int:pk>/modifier/", views.classe_update, name="classe_update"),
    path("admin_classes/<int:pk>/supprimer/", views.classe_delete, name="classe_delete"),

    # -------------------------------
    # ADMIN CRUD - ÉTUDIANTS
    # -------------------------------
    path("admin_etudiants/", views.etudiant_list, name="etudiant_list"),
    path("admin_etudiants/ajouter/", views.etudiant_create, name="etudiant_create"),
    path("admin_etudiants/<int:pk>/modifier/", views.etudiant_update, name="etudiant_update"),
    path("admin_etudiants/<int:pk>/supprimer/", views.etudiant_delete, name="etudiant_delete"),
    path("admin_etudiants/importer/", views.admin_importer_etudiants, name="admin_importer_etudiants"),

    # -------------------------------
    # ADMIN CRUD - COURS
    # -------------------------------
    path("admin_cours/", views.admin_cours_list, name="admin_cours_list"),
    path("admin_cours/ajouter/", views.admin_cours_create, name="admin_cours_create"),
    path("admin_cours/<int:pk>/modifier/", views.admin_cours_update, name="admin_cours_update"),
    path("admin_cours/<int:pk>/supprimer/", views.admin_cours_delete, name="admin_cours_delete"),

    # -------------------------------
    # RECHERCHE ET FILTRES
    # -------------------------------
    path('recherche/etudiants/', views.recherche_etudiants, name="recherche_etudiants"),
    path('recherche/cours/', views.recherche_cours, name="recherche_cours"),
    path('recherche/seances/', views.recherche_seances, name="recherche_seances"),


    path('etudiant/ajouter/', views.etudiant_create, name='etudiant_create'),
    path('etudiant/<int:pk>/modifier/', views.etudiant_update, name='etudiant_update'),
    path('etudiant/<int:pk>/delete/', views.etudiant_delete, name='etudiant_delete'),
]