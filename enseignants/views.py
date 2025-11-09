from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator 
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from utilisateurs.decorators import role_required
from .forms import EnseignantForm
from .models import Enseignant


# ======================================================
# 🔹 LISTE
# ======================================================
@login_required
def enseignant_list(request):
    """Liste des enseignants actifs avec recherche et pagination"""
    enseignants = Enseignant.objects.exclude(statut='archive')

    # Recherche
    search = request.GET.get('search')
    if search:
        enseignants = enseignants.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(matricule__icontains=search) |
            Q(specialite__icontains=search)
        )

    # Filtrage par statut
    statut = request.GET.get('statut')
    if statut:
        enseignants = enseignants.filter(statut=statut)

    # Pagination
    paginator = Paginator(enseignants.order_by('nom'), 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistiques
    total_enseignants = Enseignant.objects.count()
    enseignants_actifs = Enseignant.objects.filter(statut='actif').count()
    enseignants_inactifs = Enseignant.objects.filter(statut='inactif').count()
    total_hommes = Enseignant.objects.filter(sexe='M').count()
    total_femmes = Enseignant.objects.filter(sexe='F').count()

    return render(request, 'enseignants/enseignants.html', {
        'enseignants': page_obj,
        'total_enseignants': total_enseignants,
        'enseignants_actifs': enseignants_actifs,
        'enseignants_inactifs': enseignants_inactifs,
        'total_hommes': total_hommes,
        'total_femmes': total_femmes,
    })


# ======================================================
# 🔹 CREATE
# ======================================================
@role_required(['admin', 'directeur'])
def create_enseignant(request):
    """Créer un nouvel enseignant"""
    if request.method == 'POST':
        form = EnseignantForm(request.POST, request.FILES)
        if form.is_valid():
            enseignant = form.save(commit=False)
            enseignant.cree_par = request.user
            enseignant.statut = 'actif'
            enseignant.save()
            form.save_m2m()
            messages.success(request, f"L'enseignant {enseignant.nom} {enseignant.prenom} a été ajouté avec succès.")
            return redirect('enseignants:enseignants')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = EnseignantForm()

    return render(request, 'enseignants/ajouter_enseignant.html', {'form': form})


# ======================================================
# 🔹 DETAIL
# ======================================================
@login_required
def enseignant_detail(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    return render(request, 'enseignants/enseignant_detail.html', {'enseignant': enseignant})


# ======================================================
# 🔹 UPDATE
# ======================================================
@role_required(['admin', 'directeur', 'secretaire'])
def enseignant_update(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)

    # Bloquer Archives
    if request.user.role == 'archives':
        messages.error(request, "⛔ Vous n’avez pas la permission de modifier un enseignant.")
        return redirect('enseignants:enseignants')

    if request.method == 'POST':
        form = EnseignantForm(request.POST, request.FILES, instance=enseignant)
        if form.is_valid():
            enseignant = form.save(commit=False)
            enseignant.modifier_par = request.user
            enseignant.save()
            form.save_m2m()
            messages.success(request, "✅ Informations mises à jour avec succès !")
            return redirect('enseignants:enseignants')
        else:
            messages.error(request, "⚠️ Veuillez corriger les erreurs ci-dessous.")
    else:
        form = EnseignantForm(instance=enseignant)

    return render(request, 'enseignants/modifier_enseignant.html', {
        'form': form,
        'enseignant': enseignant
    })


# ======================================================
# 🔹 ARCHIVER
# ======================================================
@role_required(['admin', 'directeur', 'secretaire'])
def enseignant_archiver(request, pk):
    """Archive un enseignant sans suppression réelle"""
    enseignant = get_object_or_404(Enseignant, pk=pk)

    if request.user.role == 'ARCHIVES':
        messages.error(request, "⛔ Vous n’avez pas la permission d’archiver un enseignant.")
        return redirect('enseignants:enseignants')

    if enseignant.statut != 'archive':
        enseignant.statut = 'archive'
        enseignant.modifier_par = request.user
        enseignant.save()
        messages.success(request, f"📦 L'enseignant {enseignant.nom} {enseignant.prenom} a été archivé avec succès.")

    return redirect('enseignants:enseignants')


# ======================================================
# 🔹 RESTAURER
# ======================================================
@role_required(['admin', 'directeur'])
def enseignant_restaurer(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    if enseignant.statut == 'archive':
        enseignant.statut = 'actif'
        enseignant.modifier_par = request.user
        enseignant.save()
        messages.success(request, f"♻️ L'enseignant {enseignant.nom} {enseignant.prenom} a été restauré.")
    return redirect('enseignants:enseignant_archives')


# ======================================================
# 🔹 LISTE DES ARCHIVES
# ======================================================
@login_required
def enseignant_archives(request):
    enseignants_archives = Enseignant.objects.filter(statut='archive')
    return render(request, 'enseignants/enseignant_archives.html', {'enseignants': enseignants_archives})


# ======================================================
# 🔹 DELETE (Admin / Directeur uniquement)
# ======================================================
@role_required(['admin', 'directeur'])
def enseignant_delete(request, pk):
    """Supprime définitivement un enseignant (réservé Admin/Directeur)"""
    enseignant = get_object_or_404(Enseignant, pk=pk)

    # Bloque Secrétaire et Archives
    if request.user.role in ['archives', 'secretaire']:
        messages.error(request, "🚫 Vous n’avez pas la permission de supprimer cet enseignant.")
        return redirect('enseignants:enseignants')

    enseignant.delete()
    messages.success(request, f"🗑️ L'enseignant {enseignant.nom} {enseignant.prenom} a été supprimé définitivement.")
    return redirect('enseignants:enseignants')
