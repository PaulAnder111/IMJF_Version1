from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from .models import Eleve
from .forms import EleveForm
from classes.models import Classe


@login_required
def eleve_list(request):
    """Affiche la liste de tous les élèves actifs avec filtres et recherche"""
    eleves = Eleve.objects.exclude(statut='archive')  # pa montre elèv archivé yo
    classes = Classe.objects.filter(statut='actif')

    # 🔍 Recherche par nom, prénom ou matricule
    search = request.GET.get('search')
    if search:
        eleves = eleves.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(matricule__icontains=search)
        )

    # 🏫 Filtre par classe
    classe_id = request.GET.get('classe')
    if classe_id:
        eleves = eleves.filter(classe_actuelle_id=classe_id)

    # ⚙️ Filtre par statut
    statut = request.GET.get('statut')
    if statut:
        eleves = eleves.filter(statut=statut)

    # 📅 Trie par date d'inscription décroissante
    eleves = eleves.order_by('-date_inscription')

    return render(request, 'eleve_list.html', {
        'eleves': eleves,
        'classes': classes
    })


@login_required
def eleve_detail(request, pk):
    """Affiche les détails d’un élève spécifique"""
    eleve = get_object_or_404(Eleve, pk=pk)
    return render(request, 'eleves_detail.html', {'eleve': eleve})


@login_required
def eleve_update(request, pk):
    """Permet de modifier les informations d’un élève"""
    eleve = get_object_or_404(Eleve, pk=pk)

    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES, instance=eleve)
        if form.is_valid():
            form.save()
            messages.success(request, "Élève mis à jour avec succès !")
            return redirect('eleves:eleve_detail', pk=eleve.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = EleveForm(instance=eleve)

    return render(request, 'eleve_update.html', {
        'form': form,
        'eleve': eleve
    })


@login_required
@permission_required('eleves.change_eleve', raise_exception=True)
def eleve_archiver(request, pk):
    """Archive un élève au lieu de le supprimer"""
    eleve = get_object_or_404(Eleve, pk=pk)

    if eleve.statut != 'actif':
        messages.warning(request, "Seuls les élèves actifs peuvent être archivés.")
        return redirect('eleves:eleve_list')

    eleve.statut = 'archive'
    eleve.save()
    messages.success(request, f"L'élève {eleve.nom} {eleve.prenom} a été archivé avec succès.")
    return redirect('eleves:eleve_list')


@login_required
@permission_required('eleves.change_eleve', raise_exception=True)
def eleve_restaurer(request, pk):
    """Restaure un élève archivé ou suspendu"""
    eleve = get_object_or_404(Eleve, pk=pk)

    if eleve.statut not in ['archive', 'suspendu']:
        messages.warning(request, "Seuls les élèves archivés ou suspendus peuvent être restaurés.")
        return redirect('eleves:eleve_list')

    eleve.statut = 'actif'
    eleve.save()
    messages.success(request, f"L'élève {eleve.nom} {eleve.prenom} a été restauré avec succès.")
    return redirect('eleves:eleve_list')


@login_required
def eleve_archives(request):
    """Affiche la liste des élèves archivés"""
    eleves_archives = Eleve.objects.filter(statut='archive')
    return render(request, 'eleve_archiver.html', {'eleves': eleves_archives})


@login_required
def eleve_delete(request, pk):
    """Empêche la suppression directe d’un élève"""
    messages.error(request, "Suppression interdite ! Un élève ne peut être qu’archivé.")
    return redirect('eleves:eleve_list')
