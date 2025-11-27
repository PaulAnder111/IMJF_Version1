from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.core.cache import cache
from utilisateurs.decorators import role_required
from .forms import EleveForm
from .models import Eleve, HistoriqueEleve
from classes.models import Classe


import csv
from django.http import HttpResponse


# -------------------- EXPORT CSV --------------------
def export_eleve_csv(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="eleve_{eleve.matricule}.csv"'
    
    writer = csv.writer(response)
    
    writer.writerow(['SYGEE - Fiche Élève'])
    writer.writerow([])
    
    writer.writerow(['INFORMATIONS PERSONNELLES'])
    writer.writerow(['Nom', 'Prénom', 'Matricule', 'Date de naissance', 'Lieu de naissance', 'Sexe', 'Adresse'])
    writer.writerow([
        eleve.nom, 
        eleve.prenom, 
        eleve.matricule, 
        eleve.date_naissance.strftime('%d/%m/%Y') if eleve.date_naissance else '',
        eleve.lieu_naissance or 'Non renseigné',
        eleve.get_sexe_display() if hasattr(eleve, 'get_sexe_display') else eleve.sexe,
        eleve.adresse or 'Non renseigné'
    ])
    writer.writerow([])
    
    writer.writerow(['INFORMATIONS ACADÉMIQUES'])
    writer.writerow(['Niveau', 'Classe actuelle', 'Statut', 'Date inscription'])
    writer.writerow([
        eleve.niveau or 'Non renseigné',
        str(eleve.classe_actuelle) if eleve.classe_actuelle else 'Non affecté',
        eleve.get_statut_display() if hasattr(eleve, 'get_statut_display') else eleve.statut,
        eleve.date_inscription.strftime('%d/%m/%Y') if eleve.date_inscription else ''
    ])
    writer.writerow([])
    
    writer.writerow(['INFORMATIONS DE CONTACT'])
    writer.writerow(['Téléphone', 'Email', 'Nom parent', 'Téléphone parent'])
    writer.writerow([
        getattr(eleve, 'telephone', 'Non renseigné'),
        getattr(eleve, 'email', 'Non renseigné'),
        getattr(eleve, 'nom_parent', 'Non renseigné'),
        getattr(eleve, 'telephone_parent', 'Non renseigné')
    ])
    
    return response


# -------------------- LISTE OPTIMIZÉE --------------------
@login_required
def eleves_list(request):
    search_query = request.GET.get('search', '')
    statut_filter = request.GET.get('statut', '')
    classe_filter = request.GET.get('classe', '')

    eleves = Eleve.objects.select_related('classe_actuelle')

    if search_query:
        eleves = eleves.filter(Q(nom__icontains=search_query) | Q(prenom__icontains=search_query))
    if statut_filter:
        eleves = eleves.filter(statut=statut_filter)
    if classe_filter:
        eleves = eleves.filter(classe_actuelle__id=classe_filter)

    paginator = Paginator(eleves.order_by('nom'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- Statistik nan yon sèl requèt + caching ---
    cache_key_stats = "eleves_stats"
    stats = cache.get(cache_key_stats)
    if stats is None:
        stats = Eleve.objects.aggregate(
            total=Count('id'),
            actifs=Count('id', filter=Q(statut='actif')),
            suspendus=Count('id', filter=Q(statut='suspendu')),
            radies=Count('id', filter=Q(statut='radié')),
        )
        cache.set(cache_key_stats, stats, 300)

    # --- Lis klas aktif (cache) ---
    cache_key_classes = "classes_actives_list"
    classes = cache.get(cache_key_classes)
    if classes is None:
        classes = list(Classe.objects.filter(statut='actif').order_by('nom_classe'))
        cache.set(cache_key_classes, classes, 900)

    return render(request, 'eleve_list.html', {
        'eleves': page_obj,
        'classes': classes,
        'total_eleves': stats['total'],
        'eleves_actifs': stats['actifs'],
        'eleves_suspendus': stats['suspendus'],
        'eleves_radies': stats['radies'],
        'search_query': search_query,
        'statut_filter': statut_filter,
        'classe_filter': classe_filter,
    })


# -------------------- DÉTAIL OPTIMIZÉ --------------------
@login_required
def eleve_detail(request, pk):
    eleve = get_object_or_404(
        Eleve.objects.select_related('classe_actuelle', 'utilisateur'),
        pk=pk
    )
    historique = HistoriqueEleve.objects.filter(eleve=eleve).select_related('effectue_par').order_by('-date_action')
    return render(request, 'eleves_detail.html', {'eleve': eleve, 'historique': historique})


# -------------------- AJOUTER --------------------
@role_required(['admin', 'directeur', 'secretaire'])
def ajouter_eleve(request):
    classes = Classe.objects.filter(statut='actif').order_by('nom_classe')
    
    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                eleve_data = form.cleaned_data
                from enseignants.models import Enseignant
                if Enseignant.objects.filter(
                    nom__iexact=eleve_data['nom'].strip(),
                    prenom__iexact=eleve_data['prenom'].strip(),
                    date_naissance=eleve_data['date_naissance']
                ).exists():
                    messages.error(request, "Impossible d'ajouter : cette personne est déjà enregistrée comme enseignant.")
                    return redirect('eleves:ajouter_eleve')

                eleve = form.save(commit=False)
                annee_courante = datetime.now().year
                dernier_eleve = Eleve.objects.filter(
                    matricule__startswith=f"ELEVE{annee_courante}"
                ).order_by('-matricule').first()

                if dernier_eleve:
                    dernier_numero = int(dernier_eleve.matricule[-4:])
                    nouveau_numero = dernier_numero + 1
                else:
                    nouveau_numero = 1

                eleve.matricule = f"ELEVE{annee_courante}{nouveau_numero:04d}"
                eleve.save()

                HistoriqueEleve.objects.create(
                    eleve=eleve,
                    action='inscription',
                    description=f"Nouvelle inscription dans la classe {eleve.classe_actuelle}",
                    effectue_par=request.user
                )

                messages.success(request, f"L'élève {eleve.nom} {eleve.prenom} a été ajouté avec succès.")
                return redirect('eleves:eleve_list')

            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout : {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = EleveForm()

    return render(request, 'add_eleves.html', {'form': form, 'classes': classes})


# -------------------- MODIFIER (KOREKTE BUG REDIRECT) --------------------
@role_required(['admin', 'directeur', 'secretaire'])
def eleve_update(request, pk):
    eleve = get_object_or_404(
        Eleve.objects.select_related('classe_actuelle'),
        pk=pk
    )
    ancienne_classe = eleve.classe_actuelle
    classes = Classe.objects.filter(statut='actif').order_by('nom_classe')

    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES, instance=eleve)
        if form.is_valid():
            eleve_modifie = form.save(commit=False)

            if ancienne_classe != eleve_modifie.classe_actuelle:
                HistoriqueEleve.objects.create(
                    eleve=eleve,
                    action='changement_classe',
                    description=f"L'élève a été déplacé de {ancienne_classe} à {eleve_modifie.classe_actuelle}",
                    effectue_par=request.user
                )

            eleve_modifie.save()
            messages.success(request, "✅ Les informations de l'élève ont été mises à jour.")
            return redirect('eleves:eleve_list')  # 👈 BUG KOREKTE: pa gen `pk` nan URL lan
        else:
            messages.error(request, "Erreurs dans le formulaire.")
    else:
        form = EleveForm(instance=eleve)

    return render(request, 'eleve_update.html', {
        'form': form, 
        'eleve': eleve,
        'classes': classes
    })


# -------------------- ARCHIVER --------------------
@role_required(['admin', 'directeur', 'secretaire'])
def eleve_archiver(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    if eleve.statut == 'archive':
        messages.warning(request, "Cet élève est déjà archivé.")
    else:
        eleve.statut = 'archive'
        eleve.save()
        messages.success(request, f"L’élève {eleve.nom} {eleve.prenom} a été archivé.")
    return redirect('eleves:eleve_list')


# -------------------- RESTAURER --------------------
@role_required(['admin', 'directeur'])
def eleve_restaurer(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    if eleve.statut == 'archive':
        eleve.statut = 'actif'
        eleve.save()
        messages.success(request, f"✅ L’élève {eleve.nom} {eleve.prenom} a été restauré.")
    return redirect('eleves:eleve_list')


# -------------------- LISTE ARCHIVES OPTIMIZÉE --------------------
@login_required
def eleve_archives(request):
    eleves = Eleve.objects.filter(statut='archive').select_related('classe_actuelle')
    return render(request, 'eleve_archiver.html', {'eleves': eleves})


# -------------------- SUPPRIMER --------------------
@role_required(['admin', 'directeur'])
def eleve_delete(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    nom_complet = f"{eleve.nom} {eleve.prenom}"
    eleve.delete()
    messages.success(request, f"L’élève {nom_complet} a été supprimé définitivement.")
    return redirect('eleves:eleve_list')