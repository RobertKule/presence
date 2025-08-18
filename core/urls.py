from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('signup/', views.signup_view, name="signup"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),

    # CRUD des cours
    path('cours/', views.cours_list, name="cours_list"),
    path('cours/ajouter/', views.cours_create, name="cours_create"),
    path('cours/<int:pk>/modifier/', views.cours_update, name="cours_update"),
    path('cours/<int:pk>/supprimer/', views.cours_delete, name="cours_delete"),

    # CRUD des séances
    path('seances/', views.seance_list, name="seance_list"),
    path('seances/ajouter/', views.seance_create, name="seance_create"),
    path('seances/<int:pk>/modifier/', views.seance_update, name="seance_update"),
    path('seances/<int:pk>/supprimer/', views.seance_delete, name="seance_delete"),

    path('seances/<int:seance_id>/appel/', views.appel_presence, name="appel_presence"),

    path('statistiques/', views.statistiques, name="statistiques"),
    path('export/<int:cours_id>/', views.export_excel, name="export_excel"),

    path('statistiques/<int:cours_id>/pdf/', views.export_pdf_statistiques, name="export_pdf_statistiques"),

]
