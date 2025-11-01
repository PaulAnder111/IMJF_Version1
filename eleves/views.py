from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from .forms import EleveForm
from .models import Eleve
from inscriptions.models import HistoriqueClasses
from classes.models import Classe
from django.core.paginator import Paginator

# --- LIST ELEVE ---
def eleves_list(request):
    search_query = request.GET.get('search', '')
    statut_filter = request.GET.get('statut', '')
    classe_filter = request.GET.get('classe', '')

    eleves = Eleve.objects.select_related('classe_actuelle').all()

    if search_query:
        eleves = eleves.filter(nom__icontains=search_query) | eleves.filter(prenom__icontains=search_query)

    if statut_filter:
        eleves = eleves.filter(statut=statut_filter)

    if classe_filter:
        eleves = eleves.filter(classe_actuelle__id=classe_filter)

    paginator = Paginator(eleves.order_by('nom'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_eleves = Eleve.objects.count()
    eleves_actifs = Eleve.objects.filter(statut='actif').count()
    eleves_suspendus = Eleve.objects.filter(statut='suspendu').count()
    eleves_radies = Eleve.objects.filter(statut='radié').count()

    context = {
        'eleves': page_obj,
        'classes': Classe.objects.all(),
        'total_eleves': total_eleves,
        'eleves_actifs': eleves_actifs,
        'eleves_suspendus': eleves_suspendus,
        'eleves_radies': eleves_radies,
    }
    return render(request, 'eleve_list.html', context)


# --- DETAIL ELEVE ---
@login_required
def eleve_detail(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    # Récupère l'historique des classes pour cet élève
    historique = HistoriqueClasses.objects.filter(eleve=eleve).order_by('-date_change')
    return render(request, 'eleves_detail.html', {
        'eleve': eleve,
        'historique_classes': historique
    })


# --- UPDATE ELEVE ---
@login_required
def eleve_update(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES, instance=eleve)
        if form.is_valid():
            # Vérifie si la classe change
            classe_prec = eleve.classe_actuelle
            eleve = form.save()
            if classe_prec != eleve.classe_actuelle:
                HistoriqueClasses.objects.create(
                    eleve=eleve,
                    classe=eleve.classe_actuelle,
                    annee_scolaire="{}-{}".format(eleve.date_created.year, eleve.date_created.year+1)
                )
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


# --- ARCHIVER / RESTAURER / DELETE ---
@login_required
@permission_required('eleves.change_eleve', raise_exception=True)
def eleve_archiver(request, pk):
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
    eleves_archives = Eleve.objects.filter(statut='archive')
    return render(request, 'eleve_archiver.html', {'eleves': eleves_archives})


@login_required
def eleve_delete(request, pk):
    messages.error(request, "Suppression interdite ! Un élève ne peut être qu’archivé.")
    return redirect('eleves:eleve_list')


# --- HISTORIQUE DES CLASSES POUR UN ELEVE ---
@login_required
def eleve_historique(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    historique = HistoriqueClasses.objects.filter(eleve=eleve).order_by('-date_change')
    return render(request, 'eleve_historique.html', {
        'eleve': eleve,
        'historique_classes': historique
    })
