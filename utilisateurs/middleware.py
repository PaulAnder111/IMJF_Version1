from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from utilisateurs.models import UserSession

class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Track user session
        if request.user.is_authenticated:
            self._track_session(request)
        
        response = self.get_response(request)
        return response

    def _track_session(self, request):
        """Track user login/logout activity"""
        session_key = request.session.session_key
        if not session_key:
            return
        
        # Get or create session record
        try:
            session, created = UserSession.objects.get_or_create(
                session_key=session_key,
                defaults={
                    'user': request.user,
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
                }
            )
            
            # Update if inactive (user reconnecting)
            if not session.is_active:
                session.is_active = True
                session.logout_time = None
                session.save()
        except Exception as e:
            # Silently fail to avoid breaking requests
            pass

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

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