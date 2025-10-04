from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import CustomUser
from .forms import LoginForm, UserCreationForm, UserUpdateForm
from .decorators import admin_required

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenue {user.username}!")
            return redirect_to_dashboard(user)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'utilisateurs/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('utilisateurs:login')  # ✅ Ajoute 'utilisateurs:'

def redirect_to_dashboard(user):
    """Fonksyon èd pou redirije itilizatè a nan bon dashboard la"""
    if user.role == 'admin':
        return redirect('utilisateurs:dash_admin')  # ✅ Chanje 'dash_admin'
    elif user.role == 'secretaire':
        return redirect('utilisateurs:dash_secretaire')  # ✅ Chanje 'dash_secretaire'
    elif user.role == 'directeur':
        return redirect('utilisateurs:directeur_required')  # ✅ Chanje 'dash_directeur'
    elif user.role == 'enseignant':
        return redirect('utilisateurs:dashboard_teacher')  # ✅ Chanje 'dash_enseignant'
    return redirect('utilisateurs:login')  # ✅ Ajoute 'utilisateurs:'

@login_required
@admin_required
def dashboard(request):
    users_count = CustomUser.objects.count()
    enseignants_count = CustomUser.objects.filter(role='enseignant').count()
    secretaire_count = CustomUser.objects.filter(role='secretaire').count()
    directeur_count = CustomUser.objects.filter(role='directeur').count()
    
    context = {
        'users_count': users_count,
        'enseignants_count': enseignants_count,
        'secretaire_count': secretaire_count,
        'directeur_count': directeur_count,
    }
    return render(request, 'utilisateurs/dash_admin.html', context)

@login_required
def base(request):
    return render(request, 'utilisateurs/base.html')

@login_required
def secretaire_required(request):
    return render(request, 'utilisateurs/dash_secretaire.html')
  
@login_required
def directeur_required(request):
    return render(request, 'utilisateurs/dash_directeur.html')

@login_required
def dashboard_teacher(request):
    return render(request, 'utilisateurs/dash_teacher.html')

@login_required
@admin_required
def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Utilisateur {user.username} créé avec succès!")
            return redirect('utilisateurs:list_users')  # ✅ Ajoute 'utilisateurs:'
    else:
        form = UserCreationForm()
    
    return render(request, 'utilisateurs/create_user.html', {'form': form})

@login_required
@admin_required
def update_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Utilisateur {user.username} modifié avec succès!")
            return redirect('utilisateurs:list_users')  # ✅ Ajoute 'utilisateurs:'
    else:
        form = UserUpdateForm(instance=user)
    
    return render(request, 'utilisateurs/update_user.html', {'form': form, 'user': user})

@login_required
@admin_required
def list_users(request):
    users = CustomUser.objects.all().order_by('-date_created')
    return render(request, 'utilisateurs/list_users.html', {'users': users})


@login_required
@admin_required
def delete_user(request, user_id):
    """Supprimer un utilisateur"""
    user_to_delete = get_object_or_404(CustomUser, id=user_id)
    
    # Empêcher l'utilisateur de supprimer son propre compte
    if user_to_delete.id == request.user.id:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('utilisateurs:list_users')
    
    username = user_to_delete.username
    user_to_delete.delete()
    
    messages.success(request, f"L'utilisateur {username} a été supprimé avec succès.")
    return redirect('utilisateurs:list_users')

@login_required
@admin_required
def toggle_user_status(request, user_id):
    """Activer/Désactiver un utilisateur"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Empêcher l'utilisateur de désactiver son propre compte
    if user.id == request.user.id and request.POST.get('is_active') == 'false':
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect('utilisateurs:list_users')
    
    user.is_active = (request.POST.get('is_active') == 'true')
    user.save()
    
    status = "activé" if user.is_active else "désactivé"
    messages.success(request, f"L'utilisateur {user.username} a été {status} avec succès.")
    return redirect('utilisateurs:list_users')