# enseignants/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator 
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from .forms import EnseignantForm
from .models import Enseignant

# -------------------- LIST --------------------
@login_required
def enseignant_list(request):
    """Liste tous les enseignants actifs avec recherche, filtres et pagination"""
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

    # Filtre statut
    statut = request.GET.get('statut')
    if statut:
        enseignants = enseignants.filter(statut=statut)

    # Pagination
    paginator = Paginator(enseignants.order_by('nom'), 10)
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


# -------------------- CREATE --------------------
@login_required
def create_enseignant(request):
    """Créer un nouvel enseignant avec trasabilité"""
    if request.method == 'POST':
        form = EnseignantForm(request.POST, request.FILES)
        if form.is_valid():
            enseignant = form.save(commit=False)
            enseignant.cree_par = request.user
            enseignant.statut = 'actif'
            enseignant.save()
            messages.success(request, f"L'enseignant {enseignant.nom} {enseignant.prenom} ajouté avec succès.")
            return redirect('enseignants:enseignants')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = EnseignantForm()
    return render(request, 'enseignants/ajouter_enseignant.html', {'form': form})


# -------------------- DETAIL --------------------
@login_required
def enseignant_detail(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    return render(request, 'enseignants/enseignant_detail.html', {'enseignant': enseignant})


# -------------------- UPDATE --------------------
@login_required
def enseignant_update(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    if request.method == 'POST':
        form = EnseignantForm(request.POST, request.FILES, instance=enseignant)
        if form.is_valid():
            enseignant = form.save(commit=False)
            enseignant.modifier_par = request.user
            enseignant.save()
            messages.success(request, "Informations mises à jour avec succès !")
            return redirect('enseignants:enseignant_detail', pk=enseignant.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = EnseignantForm(instance=enseignant)
    return render(request, 'enseignants/modifier_enseignant.html', {'form': form, 'enseignant': enseignant})


# -------------------- ARCHIVE --------------------
@login_required
@permission_required('enseignants.change_enseignant', raise_exception=True)
def enseignant_archiver(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    if enseignant.statut != 'archive':
        enseignant.statut = 'archive'
        enseignant.modifier_par = request.user
        enseignant.save()
        messages.success(request, f"L'enseignant {enseignant.nom} {enseignant.prenom} archivé.")
    return redirect('enseignants:enseignants')


# -------------------- RESTAURE --------------------
@login_required
@permission_required('enseignants.change_enseignant', raise_exception=True)
def enseignant_restaurer(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    if enseignant.statut == 'archive':
        enseignant.statut = 'actif'
        enseignant.modifier_par = request.user
        enseignant.save()
        messages.success(request, f"L'enseignant {enseignant.nom} {enseignant.prenom} restauré.")
    return redirect('enseignants:enseignant_archives')


# -------------------- LIST ARCHIVES --------------------
@login_required
def enseignant_archives(request):
    enseignants_archives = Enseignant.objects.filter(statut='archive')
    return render(request, 'enseignants/enseignant_archives.html', {'enseignants': enseignants_archives})


# -------------------- DELETE (JS) --------------------
@login_required
@permission_required('enseignants.change_enseignant', raise_exception=True)
def enseignant_delete(request, pk):
    """Ne supprime pas mais archive avec confirmation JS"""
    enseignant = get_object_or_404(Enseignant, pk=pk)
    if enseignant.statut != 'archive':
        enseignant.statut = 'archive'
        enseignant.modifier_par = request.user
        enseignant.save()
        messages.success(request, f"L'enseignant {enseignant.nom} {enseignant.prenom} archivé via bouton Delete.")
    return redirect('enseignants:enseignants')
