from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def role_required(roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                messages.error(request, "⛔ Ou pa gen otorizasyon pou aksè nan seksyon sa.")
                return redirect('unauthorized')  # paj erè pèsonalize
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

from django.shortcuts import redirect
from django.contrib import messages

def role_required(roles):
    """Décorateur pou verifye si itilizatè gen youn nan wòl yo"""
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('utilisateurs:login')
            if request.user.role not in roles:
                messages.error(request, "vous n'avez pas acces a cette page.")
                return redirect('utilisateurs:unauthorized')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# --- Dekoratè senp pou chak wòl ---
def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)

def directeur_required(view_func):
    return role_required(['DIRECTEUR', 'ADMIN'])(view_func)

def secretaire_required(view_func):
    return role_required(['SECRETAIRE', 'DIRECTEUR', 'ADMIN'])(view_func)

def archive_required(view_func):
    return role_required(['ARCHIVE', 'ADMIN', 'DIRECTEUR','SECRETAIRE'])(view_func)

