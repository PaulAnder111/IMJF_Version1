from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Eleve
from .forms import EleveForm
from classes.models import Classe


@login_required
def eleve_list(request):
    """Affiche la liste de tous les élèves avec filtres et recherche"""
    eleves = Eleve.objects.all()
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
    return render(request, 'eleve_detail.html', {'eleve': eleve})


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

    return render(request, 'eleves/eleve_detail.html', {
        'form': form,
        'eleve': eleve
    })


@login_required
def eleve_delete(request, pk):
    """Supprime un élève de la base de données"""
    eleve = get_object_or_404(Eleve, pk=pk)

    if request.method == 'POST':
        eleve.delete()
        messages.success(request, "Élève supprimé avec succès !")
        return redirect('eleves:eleve_list')

    # Optionnel : page de confirmation avant suppression
    return render(request, 'eleves/eleve_confirm_delete.html', {'eleve': eleve})
