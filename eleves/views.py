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
from annee_scolaire.models import AnneeScolaire
import random



# -------------------- PAGE D'EXPORTATION --------------------
@login_required
def exportation_eleves(request):
    classe_id = request.GET.get('classe')

    try:
        annee_actuelle = AnneeScolaire.objects.get(est_annee_courante=True)
    except AnneeScolaire.DoesNotExist:
        annee_actuelle = None

    base_eleves = Eleve.objects.select_related(
        'classe_actuelle', 
        'annee_scolaire'
    )

    # 🔥 AJOUTER LE MÊME FILTRE QUE DANS LA LISTE
    if annee_actuelle:
        base_eleves = base_eleves.filter(annee_scolaire=annee_actuelle)

    if classe_id:
        eleves = base_eleves.filter(classe_actuelle__id=classe_id)
    else:
        eleves = base_eleves

    eleves = eleves.order_by('nom', 'prenom')

    total_count = eleves.count()
    actif_count = eleves.filter(statut='actif').count()
    suspendu_count = eleves.filter(statut='suspendu').count()
    radie_count = eleves.filter(statut='radié').count()

    classes = Classe.objects.filter(statut='actif').order_by('nom_classe')

    return render(request, 'export_modal.html', {
        'eleves': eleves,
        'classes': classes,
        'annee_actuelle': annee_actuelle,
        'total_count': total_count,
        'actif_count': actif_count,
        'suspendu_count': suspendu_count,
        'radie_count': radie_count,
    })



# -------------------- LISTE OPTIMIZÉE AVEC ANNEE SCOLAIRE --------------------
@login_required
def eleves_list(request):
    search_query = request.GET.get('search', '')
    statut_filter = request.GET.get('statut', '')
    classe_filter = request.GET.get('classe', '')

    # === KORIKSYON: Chanje 'est_actuelle' pou 'est_annee_courante' ===
    try:
        annee_actuelle = AnneeScolaire.objects.get(est_annee_courante=True)
    except AnneeScolaire.DoesNotExist:
        annee_actuelle = None
        messages.warning(request, "Aucune année scolaire active. Veuillez en sélectionner une.")

    # Filtrer par annee scolaire si li egziste
    if annee_actuelle:
        eleves = Eleve.objects.select_related('classe_actuelle').filter(annee_scolaire=annee_actuelle)
    else:
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

    # --- Statistik ak cache ki konsidere annee scolaire ---
    cache_key_stats = f"eleves_stats_{annee_actuelle.id if annee_actuelle else 'no_annee'}"
    stats = cache.get(cache_key_stats)
    if stats is None:
        base_queryset = eleves  # Deja filtre par annee scolaire si egziste
        stats = base_queryset.aggregate(
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
        'annee_actuelle': annee_actuelle,
    })


# -------------------- DÉTAIL OPTIMIZÉ --------------------
@login_required
def eleve_detail(request, pk):
    eleve = get_object_or_404(
        Eleve.objects.select_related('classe_actuelle', 'annee_scolaire'),  # 👈 Chanje isit la
         pk=pk
    )
    historique = HistoriqueEleve.objects.filter(eleve=eleve).select_related('effectue_par').order_by('-date_action')
    
    # KORIKSYON: Chanje 'est_actuelle' pou 'est_annee_courante'
    try:
        annee_actuelle = AnneeScolaire.objects.get(est_annee_courante=True)
    except AnneeScolaire.DoesNotExist:
        annee_actuelle = None
        
    return render(request, 'eleves_detail.html', {
        'eleve': eleve, 
        'historique': historique,
        'annee_actuelle': annee_actuelle
    })


# -------------------- AJOUTER AVEC ANNEE SCOLAIRE --------------------
@role_required(['admin', 'directeur', 'secretaire'])
def ajouter_eleve(request):
    classes = Classe.objects.filter(statut='actif').order_by('nom_classe')
    
    # KORIKSYON: Chanje 'est_actuelle' pou 'est_annee_courante'
    try:
        annee_actuelle = AnneeScolaire.objects.get(est_annee_courante=True)
    except AnneeScolaire.DoesNotExist:
        annee_actuelle = None
        messages.error(request, "Aucune année scolaire active. Impossible d'ajouter un élève.")
        return redirect('eleves:eleve_list')
    
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
                
                # Asigne annee scolaire actuelle
                eleve.annee_scolaire = annee_actuelle
                
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
                    description=f"Nouvelle inscription dans la classe {eleve.classe_actuelle} pour l'année {annee_actuelle.nom}",
                    effectue_par=request.user
                )

                messages.success(request, f"L'élève {eleve.nom} {eleve.prenom} a été ajouté avec succès pour l'année {annee_actuelle.nom}.")
                return redirect('eleves:eleve_list')

            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout : {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = EleveForm()

    return render(request, 'add_eleves.html', {
        'form': form, 
        'classes': classes,
        'annee_actuelle': annee_actuelle
    })


# -------------------- MODIFIER AVEC ANNEE SCOLAIRE --------------------
@role_required(['admin', 'directeur', 'secretaire'])
def eleve_update(request, pk):
    eleve = get_object_or_404(
        Eleve.objects.select_related('classe_actuelle'),
        pk=pk
    )
    ancienne_classe = eleve.classe_actuelle
    classes = Classe.objects.filter(statut='actif').order_by('nom_classe')

    # KORIKSYON: Chanje 'est_actuelle' pou 'est_annee_courante'
    try:
        annee_actuelle = AnneeScolaire.objects.get(est_annee_courante=True)
    except AnneeScolaire.DoesNotExist:
        annee_actuelle = None

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
            return redirect('eleves:eleve_list')
        else:
            messages.error(request, "Erreurs dans le formulaire.")
    else:
        form = EleveForm(instance=eleve)

    return render(request, 'eleve_update.html', {
        'form': form, 
        'eleve': eleve,
        'classes': classes,
        'annee_actuelle': annee_actuelle
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
        messages.success(request, f"L'élève {eleve.nom} {eleve.prenom} a été archivé.")
    return redirect('eleves:eleve_list')


# -------------------- RESTAURER --------------------
@role_required(['admin', 'directeur'])
def eleve_restaurer(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    if eleve.statut == 'archive':
        eleve.statut = 'actif'
        eleve.save()
        messages.success(request, f"✅ L'élève {eleve.nom} {eleve.prenom} a été restauré.")
    return redirect('eleves:eleve_list')


# -------------------- LISTE ARCHIVES OPTIMIZÉE --------------------
@login_required
def eleve_archives(request):
    eleves = Eleve.objects.filter(statut='archive').select_related('classe_actuelle')
    
    # KORIKSYON: Chanje 'est_actuelle' pou 'est_annee_courante'
    try:
        annee_actuelle = AnneeScolaire.objects.get(est_annee_courante=True)
    except AnneeScolaire.DoesNotExist:
        annee_actuelle = None
        
    return render(request, 'eleve_archiver.html', {
        'eleves': eleves,
        'annee_actuelle': annee_actuelle
    })


# -------------------- SUPPRIMER --------------------
@role_required(['admin', 'directeur'])
def eleve_delete(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    nom_complet = f"{eleve.nom} {eleve.prenom}"
    eleve.delete()
    messages.success(request, f"L'élève {nom_complet} a été supprimé définitivement.")
    return redirect('eleves:eleve_list')