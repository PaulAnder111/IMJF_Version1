from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser, AuditLog
from .decorators import admin_required

# ✅ Fonksyon pou log aksyon kritik yo
def log_action(actor, action, target=None, details=None):
    AuditLog.objects.create(
        actor=actor,
        action=action,
        target=target,
        details=details or {}
    )

# ----------------------- LOGIN / LOGOUT -----------------------
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = CustomUser.objects.filter(username=username).first()

        # 🚨 Tcheke si kont lan locké
        if user and user.is_locked():
            messages.error(request, "Votre compte est temporairement bloqué suite à plusieurs tentatives échouées.")
            return redirect('utilisateurs:login')

        auth_user = authenticate(request, username=username, password=password)

        if auth_user is not None:
            auth_user.reset_failed_logins()

            # ✅ Tcheke si itilizatè dwe chanje modpas
            if auth_user.must_change_password:
                login(request, auth_user)
                messages.warning(request, "Vous devez changer votre mot de passe avant de continuer.")
                return redirect('utilisateurs:password_change')

            login(request, auth_user)
            log_action(auth_user, "login_success")
            return redirect_to_dashboard(auth_user)
        else:
            if user:
                user.register_failed_login()
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'utilisateurs/login.html')


@login_required
def logout_view(request):
    if request.user.is_authenticated:
        log_action(request.user, "logout")
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('utilisateurs:login')


# ----------------------- DASHBOARD -----------------------
def redirect_to_dashboard(user):
    # Tout itilizatè ale nan menm dashboard
    return redirect('utilisateurs:dash_admin')


def base(request):
    return render(request, "utilisateurs/base.html")


@login_required
def dashboard(request):
    users_count = CustomUser.objects.count()
    archives_count = CustomUser.objects.filter(role='archives').count()
    secretaire_count = CustomUser.objects.filter(role='secretaire').count()
    directeur_count = CustomUser.objects.filter(role='directeur').count()

    modules = [
        {"nom": "Inscriptions", "icon": "fa-clipboard-user"},
        {"nom": "Élèves", "icon": "fa-user-graduate"},
        {"nom": "Enseignants", "icon": "fa-chalkboard-teacher"},
        {"nom": "Classes", "icon": "fa-school"},
        {"nom": "Matières", "icon": "fa-book-open"},
        {"nom": "Cours", "icon": "fa-chalkboard"},
        {"nom": "Utilisateurs", "icon": "fa-users-cog"},
    ]

    context = {
        'users_count': users_count,
        'archives_count': archives_count,
        'secretaire_count': secretaire_count,
        'directeur_count': directeur_count,
        'modules': modules,
        'role': request.user.role
    }

    return render(request, "utilisateurs/dash_admin.html", context)


# ----------------------- UTILISATEURS -----------------------
@login_required
@admin_required
def create_user(request):
    if request.method == 'POST':
        form = CustomUser(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            log_action(request.user, "create_user", target=user.username)
            messages.success(request, f"Utilisateur {user.username} créé avec succès!")
            return redirect('utilisateurs:list_users')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = CustomUser()

    return render(request, 'utilisateurs/create_user.html', {'form': form})


@login_required
@admin_required
def update_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = AuditLog(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            log_action(request.user, "update_user", target=user.username)
            messages.success(request, f"Utilisateur {user.username} mis à jour avec succès!")
            return redirect('utilisateurs:list_users')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = AuditLog(instance=user)

    return render(request, 'utilisateurs/update_user.html', {'form': form, 'user': user})


@login_required
@admin_required
def list_users(request):
    users = CustomUser.objects.all().order_by('-date_created')
    return render(request, 'utilisateurs/list_users.html', {'users': users})


@login_required
@admin_required
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(CustomUser, id=user_id)

    if user_to_delete.id == request.user.id:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('utilisateurs:list_users')

    username = user_to_delete.username
    user_to_delete.delete()
    log_action(request.user, "delete_user", target=username)
    messages.success(request, f"L'utilisateur {username} a été supprimé avec succès.")
    return redirect('utilisateurs:list_users')


@login_required
@admin_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if user.id == request.user.id and request.POST.get('is_active') == 'false':
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect('utilisateurs:list_users')

    user.is_active = (request.POST.get('is_active') == 'true')
    user.save()
    status = "activé" if user.is_active else "désactivé"
    log_action(request.user, "toggle_user_status", target=user.username, details={"status": status})
    messages.success(request, f"L'utilisateur {user.username} a été {status} avec succès.")
    return redirect('utilisateurs:list_users')


@login_required
def view_user(request, user_id):
    utilisateur = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'utilisateurs/afficher.html', {'utilisateur': utilisateur})


# ----------------------- CHANGER FOTO / MODPAS -----------------------
@login_required
def change_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        user = request.user
        user.photo = request.FILES['photo']
        user.save()
        messages.success(request, "Photo de profil mise à jour avec succès.")
    else:
        messages.error(request, "Erreur lors de la mise à jour de la photo.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Mot de passe changé avec succès.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ----------------------- NOUVEAU : HISTORIQUE DES UTILISATEURS -----------------------
@login_required
@admin_required
def historique_utilisateur(request, user_id):
    """
    Afiche tout chanjman ki fèt sou yon itilizatè espesifik.
    """
    utilisateur = get_object_or_404(CustomUser, id=user_id)
    historique = utilisateur.historiqueClasses.all().order_by('-history_date')
    return render(request, 'utilisateurs/historique_utilisateur.html', {
        'utilisateur': utilisateur,
        'historique': historique,
    })


@login_required
@admin_required
def historique_global(request):
    """
    Afiche tout chanjman sou tout itilizatè yo.
    """
    from simple_history.utils import get_history_model_for_model
    HistoryUser = get_history_model_for_model(CustomUser)
    historique = HistoryUser.objects.select_related('history_user').order_by('-history_date')[:100]

    return render(request, 'utilisateurs/historique_global.html', {
        'historique': historique
    })
