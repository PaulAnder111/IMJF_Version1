# enseignants/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator 
from django.contrib.auth.decorators import login_required, permission_required
from .forms import EnseignantForm
from django.db.models import Q
from .models import Enseignant

@login_required
def enseignant_list(request):
    """Liste tous les enseignants actifs avec recherche, filtres, statistiques et pagination"""

    # 🧑‍🏫 Liste des enseignants (sauf archivés)
    enseignants = Enseignant.objects.exclude(statut='archive')

    # 🔍 Recherche
    search = request.GET.get('search')
    if search:
        enseignants = enseignants.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(matricule__icontains=search) |
            Q(specialite__icontains=search)
        )

    # ⚙️ Filtre par statut
    statut = request.GET.get('statut')
    if statut:
        enseignants = enseignants.filter(statut=statut)

    # 🧮 Statistiques globales
    total_enseignants = Enseignant.objects.count()
    enseignants_actifs = Enseignant.objects.filter(statut='actif').count()
    enseignants_inactifs = Enseignant.objects.filter(statut='inactif').count()
    total_hommes = Enseignant.objects.filter(sexe='M').count()
    total_femmes = Enseignant.objects.filter(sexe='F').count()

    # 🔢 Trie alphabétique
    enseignants = enseignants.order_by('nom')

    # 📄 Pagination (10 par page)
    paginator = Paginator(enseignants, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 🧾 Rendu du template
    return render(request, 'enseignants/enseignants.html', {
        'enseignants': page_obj,
        'total_enseignants': total_enseignants,
        'enseignants_actifs': enseignants_actifs,
        'enseignants_inactifs': enseignants_inactifs,
        'total_hommes': total_hommes,
        'total_femmes': total_femmes,
    })

@login_required
def create_enseignant(request):
    """Permet d'ajouter un nouvel enseignant dans le système"""
    if request.method == 'POST':
        form = EnseignantForm(request.POST, request.FILES)
        if form.is_valid():
            enseignant = form.save(commit=False)
            enseignant.statut = 'actif'  # Par défaut, il devient actif
            enseignant.save()
            messages.success(request, f"L'enseignant {enseignant.nom} {enseignant.prenom} a été ajouté avec succès.")
            return redirect('enseignants:enseignant_list')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = EnseignantForm()

    return render(request, 'enseignants/ajouter_enseignant.html', {'form': form})



@login_required
def enseignant_detail(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    return render(request, 'enseignants/enseignant_detail.html', {'enseignant': enseignant})


@login_required
def enseignant_update(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    if request.method == 'POST':
        form = EnseignantForm(request.POST, request.FILES, instance=enseignant)
        if form.is_valid():
            form.save()
            messages.success(request, "Informations de l'enseignant mises à jour avec succès !")
            return redirect('enseignants:enseignant_detail', pk=enseignant.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = EnseignantForm(instance=enseignant)
    return render(request, 'enseignants/enseignant_update.html', {'form': form, 'enseignant': enseignant})


@login_required
@permission_required('enseignants.change_enseignant', raise_exception=True)
def enseignant_archiver(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    enseignant.statut = 'archive'
    enseignant.save()
    messages.success(request, f"L'enseignant {enseignant.nom} {enseignant.prenom} a été archivé avec succès.")
    return redirect('enseignants:enseignant_list')


@login_required
@permission_required('enseignants.change_enseignant', raise_exception=True)
def enseignant_restaurer(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    enseignant.statut = 'actif'
    enseignant.save()
    messages.success(request, f"L'enseignant {enseignant.nom} {enseignant.prenom} a été restauré avec succès.")
    return redirect('enseignants:enseignant_archives')


@login_required
def enseignant_archives(request):
    enseignants_archives = Enseignant.objects.filter(statut='archive')
    return render(request, 'enseignants/enseignant_archives.html', {'enseignants': enseignants_archives})
