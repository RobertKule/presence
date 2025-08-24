from django.shortcuts import redirect
from django.urls import reverse

class EnseignantRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Vérifier si l'utilisateur est enseignant et tente d'accéder à l'admin
        # if (request.user.is_authenticated and 
        #     request.user.role == 'enseignant' and 
        #     request.path.startswith('/admin/')):
        #     # Utilisez une URL directe au lieu d'un nom d'URL
        #     return redirect('/')  # Redirige vers la page d'accueil
        pass
        return None