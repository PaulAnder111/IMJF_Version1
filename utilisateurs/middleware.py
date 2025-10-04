from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse

class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        # URLs autorisées pour tous les utilisateurs authentifiés
        public_urls = [
            reverse('logout'),
            reverse('password_change'),
            reverse('password_change_done'),
        ]

        if request.path in public_urls:
            return None

        # Vérification des permissions par rôle
        user_role = request.user.role

        if request.path.startswith('/utilisateurs/dash_admin/') and not user_role == 'admin':
            messages.error(request, "Accès non autorisé à cette section.")
            return redirect(self.get_redirect_url(user_role))

        elif request.path.startswith('/utilisateurs/secretaire/') and user_role not in ['admin', 'secretaire']:
            messages.error(request, "Accès non autorisé à cette section.")
            return redirect(self.get_redirect_url(user_role))

        elif request.path.startswith('/utilisateurs/directeur/') and user_role not in ['admin', 'directeur']:
            messages.error(request, "Accès non autorisé à cette section.")
            return redirect(self.get_redirect_url(user_role))

        elif request.path.startswith('/utilisateurs/teacher/') and user_role not in ['admin', 'enseignant']:
            messages.error(request, "Accès non autorisé à cette section.")
            return redirect(self.get_redirect_url(user_role))

        return None

    def get_redirect_url(self, role):
        if role == 'admin':
            return '/utilisateurs/dash_admin/'
        elif role == 'directeur':
            return '/utilisateurs/directeur/'
        elif role == 'secretaire':
            return '/utilisateurs/secretaire/'
        elif role == 'enseignant':
            return '/utilisateurs/enseignant/'
        return '/login/'