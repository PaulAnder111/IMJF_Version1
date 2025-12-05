# utilisateurs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .forms import CustomUserUpdateForm, CustomUserCreationForm
from django.conf import settings
from .forms import CustomUserCreationForm
from .models import CustomUser, AuditLog
from .decorators import admin_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.core.cache import cache
from inscriptions.models import Inscription
from eleves.models import Eleve
from enseignants.models import Enseignant
from classes.models import Classe
from matieres.models import Matiere
from cours.models import Cours

User = get_user_model()

# Yon diksyonè tanporè pou kenbe kòd reset yo (pou dev/testing)
RESET_CODES = {}


# ==========================================================
# Fonksyon pou log aksyon kritik
# ==========================================================
def log_action(actor, action, target=None, details=None):
    AuditLog.objects.create(
        actor=actor,
        action=action,
        target=target,
        details=details or {}
    )

# ==========================================================
# LOGIN / LOGOUT
# ==========================================================
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('utilisateurs:dash_admin')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = CustomUser.objects.filter(username=username).first()

        if user and user.is_locked():
            messages.error(request, "Votre compte est temporairement bloqué suite à plusieurs tentatives échouées.")
            return redirect('utilisateurs:login')

        auth_user = authenticate(request, username=username, password=password)
        if auth_user:
            auth_user.reset_failed_logins()
            if auth_user.must_change_password:
                login(request, auth_user)
                messages.warning(request, "Vous devez changer votre mot de passe avant de continuer.")
                return redirect('utilisateurs:change_password')

            login(request, auth_user)
            log_action(auth_user, "login_success")
            return redirect('utilisateurs:dash_admin')
        else:
            if user:
                user.register_failed_login()
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'utilisateurs/login.html')

@login_required
def logout_view(request):
    log_action(request.user, "logout")
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('utilisateurs:login')

# def db_error(request):
#     return render(request, 'utilisateurs/db_error.html')


#==================================================
#unauthorized
#====================================


def unauthorized(request):
    return render(request, 'utilisateurs/unauthorized.html')


# ==========================================================
# DASHBOARD
# ==========================================================
@login_required
def dashboard(request):
    from utilisateurs.models import UserSession
    
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)

    # Kalkile utilisateurs enligne (active sessions - real-time)
    users_online = UserSession.objects.filter(is_active=True).count()

    # Utiliser le cache pour les compteurs lourds (TTL = 300s)
    cache_key = 'dashboard_stats_v1'
    stats = cache.get(cache_key)
    if stats is None:
        stats = {
            'inscriptions_count': Inscription.objects.count(),
            'eleves_count': Eleve.objects.count(),
            'enseignants_count': Enseignant.objects.count(),
            'classes_count': Classe.objects.count(),
            'matieres_count': Matiere.objects.count(),
            'cours_count': Cours.objects.count(),
            'secretaires_count': User.objects.filter(role='secretaire').count(),
            'directeurs_count': User.objects.filter(role='directeur').count(),
            'archives_count': User.objects.filter(role='archives').count(),
            'users_count': User.objects.count(),
        }
        cache.set(cache_key, stats, 300)

    # Inscriptions recentes (toujours live, limitées)
    recent_inscriptions = Inscription.objects.filter(statut='actif').select_related('classe', 'eleve', 'cree_par').order_by('-date_created')[:5]

    # Estatistik pou bar progresyon (valeurs placeholder)
    taux_presence = 85
    classes_actives = 92
    satisfaction = 78
    performance_academique = 88

    context = {
        **stats,
        'users_online': users_online,
        'inscriptions_recentes': recent_inscriptions,
        'taux_presence': taux_presence,
        'classes_actives': classes_actives,
        'satisfaction': satisfaction,
        'performance_academique': performance_academique,
    }
    
    return render(request, 'utilisateurs/dash_admin.html', context)

# ==========================================================
# UTILISATEURS CRUD (admin)
# ==========================================================
@login_required
@admin_required
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            log_action(request.user, "create_user", target=user.username)
            messages.success(request, f"Utilisateur {user.username} créé avec succès!")
            return redirect('utilisateurs:list_users')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'utilisateurs/create_user.html', {'form': form})

@login_required
@admin_required
def list_users(request):
    users = CustomUser.objects.all().order_by('-date_created')
    return render(request, 'utilisateurs/list_users.html', {'users': users})

@login_required
@admin_required
def a_view_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'utilisateurs/afficher.html', {'user': user})

@login_required
@admin_required
def update_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            log_action(request.user, "update_user", target=user.username)
            messages.success(request, f"Utilisateur {user.username} mis à jour avec succès !")
            return redirect('utilisateurs:list_users')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = CustomUserUpdateForm(instance=user)

    return render(request, 'utilisateurs/update_user.html', {'form': form, 'user': user})

@login_required
@admin_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user.id == request.user.id:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('utilisateurs:list_users')
    username = user.username
    user.delete()
    log_action(request.user, "delete_user", target=username)
    messages.success(request, f"L'utilisateur {username} a été supprimé.")
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
    messages.success(request, f"L'utilisateur {user.username} a été {status}.")
    return redirect('utilisateurs:list_users')

# ==========================================================
# CHANGER FOTO / MODPAS
# ==========================================================
@login_required
def change_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        request.user.photo = request.FILES['photo']
        request.user.save()
        messages.success(request, "Photo de profil mise à jour.")
    else:
        messages.error(request, "Erreur lors de la mise à jour de la photo.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def update_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        if not request.user.check_password(old_password):
            messages.error(request, "Ancien mot de passe incorrect.")
        elif new_password1 != new_password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        else:
            request.user.set_password(new_password1)
            request.user.must_change_password = False
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Mot de passe mis à jour.")
            return redirect('utilisateurs:dash_admin')
    return redirect('utilisateurs:dash_admin')

# ==========================================================
# WORKFLOW RESET MODPAS POU KONT BLOKE
# ==========================================================
def send_reset_code(user, code):
    subject = "Code de réinitialisation de votre compte"
    message = f"Bonjour {user.username},\n\nVotre compte a été bloqué.\nVoici votre code de réinitialisation temporaire: {code}\n\nMerci."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

# utilisateurs/views.py (pwodwi nouvo seksyon pou reset password)
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.utils import timezone
from datetime import timedelta

# Pou voye email
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

# Yon diksyonè tanporè pou kenbe kòd reset yo (pou dev/testing)
RESET_CODES = {}

# ------------------ STEP 1: Request reset code ------------------
def request_reset_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            # Kreye kòd aleatwa 6-chif
            code = str(random.randint(100000, 999999))
            RESET_CODES[email] = {
                'code': code,
                'expires_at': timezone.now() + timedelta(minutes=10)
            }

            # Voye email (default)
            send_mail(
                subject="Code de réinitialisation de votre mot de passe",
                message=f"Bonjour {user.username},\n\nVoici votre code de réinitialisation: {code}\nCe code expirera dans 10 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

            messages.success(request, f"Un code de vérification a été envoyé à {email}.")
            return redirect('utilisateurs:verify_reset_code')
        else:
            messages.error(request, "Email non trouvé dans le système.")

    return render(request, 'utilisateurs/password_reset_request.html')


# ------------------ STEP 2: Verify code ------------------
def verify_reset_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')

        reset_info = RESET_CODES.get(email)

        if reset_info:
            if timezone.now() > reset_info['expires_at']:
                messages.error(request, "Le code a expiré. Veuillez redemander un nouveau code.")
                del RESET_CODES[email]
            elif code == reset_info['code']:
                messages.success(request, "Code vérifié. Vous pouvez maintenant réinitialiser votre mot de passe.")
                request.session['reset_email'] = email
                return redirect('utilisateurs:reset_password')
            else:
                messages.error(request, "Code incorrect. Veuillez réessayer.")
        else:
            messages.error(request, "Aucun code trouvé pour cet email. Veuillez redemander un code.")

    return render(request, 'utilisateurs/password_reset_verify.html')


# ------------------ STEP 3: Reset password ------------------
def reset_password(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, "Aucune session de réinitialisation active.")
        return redirect('utilisateurs:request_reset_code')

    user = User.objects.filter(email=email).first()
    if not user:
        messages.error(request, "Utilisateur introuvable.")
        return redirect('utilisateurs:request_reset_code')

    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if new_password1 != new_password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        else:
            user.set_password(new_password1)
            user.must_change_password = False
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter.")
            # Efface session reset
            if 'reset_email' in request.session:
                del request.session['reset_email']
            if email in RESET_CODES:
                del RESET_CODES[email]
            return redirect('utilisateurs:login')

    return render(request, 'utilisateurs/password_reset_new.html', {'email': email})


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Notification, NotificationRecipient

@login_required
def get_notifications(request):
    # Ensure NotificationRecipient entries exist for role-targeted or broadcast notifications
    from django.db.models import Q

    # Attach recipients on-the-fly for matching notifications that don't yet have a recipient row
    role_or_broadcast_qs = Notification.objects.filter(Q(recipient_role=request.user.role) | Q(broadcast=True))
    # exclude notifications that already have a recipient entry for this user
    role_or_broadcast_qs = role_or_broadcast_qs.exclude(recipients__user=request.user)
    for n in role_or_broadcast_qs:
        try:
            NotificationRecipient.objects.create(notification=n, user=request.user)
        except Exception:
            # ignore race conditions / unique constraint failures
            pass

    # Get recipient entries (this covers per-user notifications and attached role/broadcast ones)
    recipient_qs = NotificationRecipient.objects.filter(user=request.user).select_related('notification')
    recipient_qs = recipient_qs.order_by('-created_at')[:20]

    notifications_data = []
    for rec in recipient_qs:
        n = rec.notification
        notifications_data.append({
            'id': str(n.id),
            'type': n.type,
            'title': n.title,
            'message': n.message,
            'read': rec.read,
            'timestamp': n.created_at.isoformat(),
            'target_url': n.target_url or '#'
        })

    unread_count = NotificationRecipient.objects.filter(user=request.user, read=False).count()

    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count
    })

@login_required
@csrf_exempt
def mark_notification_read(request, notification_id):
    try:
        # Mark the recipient record as read for this user
        rec = NotificationRecipient.objects.get(notification_id=notification_id, user=request.user)
        rec.read = True
        rec.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification non trouvée'})
    except NotificationRecipient.DoesNotExist:
        # Possibly the notification exists but no recipient row was created; try to create one and mark it
        try:
            n = Notification.objects.get(id=notification_id)
            rec = NotificationRecipient.objects.create(notification=n, user=request.user, read=True)
            return JsonResponse({'success': True})
        except Exception:
            return JsonResponse({'success': False, 'error': 'Notification non trouvée'})

@login_required  
@csrf_exempt
def mark_all_notifications_read(request):
    NotificationRecipient.objects.filter(user=request.user, read=False).update(read=True)
    return JsonResponse({'success': True})


# ==========================================================
# ACTIVE USERS TRACKING (Admin pou monitore koneksyon)
# ==========================================================
@login_required
@login_required
@admin_required
def active_users_list(request):
    """Show all active user sessions with login/logout tracking"""
    from utilisateurs.models import UserSession
    from django.db.models import Q, Max
    
    # Active sessions (currently online)
    active_sessions = UserSession.objects.filter(is_active=True).select_related('user').order_by('-login_time')
    
    # Recently logged out sessions
    logged_out_sessions = UserSession.objects.filter(is_active=False).select_related('user').order_by('-logout_time')[:20]
    
    # All users with their last session info
    all_users_with_sessions = []
    for user in User.objects.all().order_by('role', 'username'):
        last_session = UserSession.objects.filter(user=user).order_by('-login_time').first()
        all_users_with_sessions.append({
            'user': user,
            'last_session': last_session,
            'is_online': user.id in [s.user.id for s in active_sessions]
        })
    
    context = {
        'active_sessions': active_sessions,
        'logged_out_sessions': logged_out_sessions,
        'all_users_with_sessions': all_users_with_sessions,
        'total_active': active_sessions.count(),
        'total_users': User.objects.count(),
    }
    
    return render(request, 'utilisateurs/active_users.html', context)


@login_required
@admin_required
def get_active_users_json(request):
    """API endpoint para sa dashboard estatistik - return active users count"""
    from utilisateurs.models import UserSession
    
    active_count = UserSession.objects.filter(is_active=True).count()
    
    return JsonResponse({
        'active_users': active_count,
        'timestamp': timezone.now().isoformat(),
    })