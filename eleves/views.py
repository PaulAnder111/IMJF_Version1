from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from utilisateurs.decorators import role_required
from .forms import EleveForm
from .models import Eleve, HistoriqueEleve
from classes.models import Classe


import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def export_eleve_csv(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="eleve_{eleve.matricule}.csv"'
    
    writer = csv.writer(response)
    
    # En-tête
    writer.writerow(['SYGEE - Fiche Élève'])
    writer.writerow([])
    
    # Informations personnelles
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
    
    # Informations académiques
    writer.writerow(['INFORMATIONS ACADÉMIQUES'])
    writer.writerow(['Niveau', 'Classe actuelle', 'Statut', 'Date inscription'])
    writer.writerow([
        eleve.niveau or 'Non renseigné',
        str(eleve.classe_actuelle) if eleve.classe_actuelle else 'Non affecté',
        eleve.get_statut_display() if hasattr(eleve, 'get_statut_display') else eleve.statut,
        eleve.date_inscription.strftime('%d/%m/%Y') if eleve.date_inscription else ''
    ])
    writer.writerow([])
    
    # Informations de contact
    writer.writerow(['INFORMATIONS DE CONTACT'])
    writer.writerow(['Téléphone', 'Email', 'Nom parent', 'Téléphone parent'])
    writer.writerow([
        getattr(eleve, 'telephone', 'Non renseigné'),
        getattr(eleve, 'email', 'Non renseigné'),
        getattr(eleve, 'nom_parent', 'Non renseigné'),
        getattr(eleve, 'telephone_parent', 'Non renseigné')
    ])
    
    return response

# -------------------- LISTE --------------------
@login_required
def eleves_list(request):
    """Liste des élèves avec recherche, filtres et pagination"""
    search_query = request.GET.get('search', '')
    statut_filter = request.GET.get('statut', '')
    classe_filter = request.GET.get('classe', '')

    eleves = Eleve.objects.select_related('classe_actuelle').all()

    # --- Filtres dynamiques ---
    if search_query:
        eleves = eleves.filter(Q(nom__icontains=search_query) | Q(prenom__icontains=search_query))
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

    return render(request, 'eleve_list.html', {
        'eleves': page_obj,
        'classes': Classe.objects.all(),
        'total_eleves': total_eleves,
        'eleves_actifs': eleves_actifs,
        'eleves_suspendus': eleves_suspendus,
        'eleves_radies': eleves_radies,
        'search_query': search_query,
        'statut_filter': statut_filter,
        'classe_filter': classe_filter,
    })


# -------------------- DETAIL --------------------
@login_required
def eleve_detail(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    historique = HistoriqueEleve.objects.filter(eleve=eleve).order_by('-date_action')
    context = {
        'eleve': eleve,
        'historique': historique,
    }
    return render(request, 'eleves_detail.html', context)


# -------------------- AJOUTER --------------------
# -------------------- AJOUTER --------------------
@role_required(['admin', 'directeur', 'secretaire'])
def ajouter_eleve(request):
    """Ajout manuel d'un élève"""
    classes = Classe.objects.filter(statut='actif').order_by('nom_classe')
    
    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                eleve_data = form.cleaned_data
                # Check if this person is already registered as an Enseignant
                from enseignants.models import Enseignant
                if Enseignant.objects.filter(
                    nom__iexact=eleve_data['nom'].strip(),
                    prenom__iexact=eleve_data['prenom'].strip(),
                    date_naissance=eleve_data['date_naissance']
                ).exists():
                    messages.error(request, "Impossible d'ajouter : cette personne est déjà enregistrée comme enseignant.")
                    return redirect('eleves:ajouter_eleve')

                eleve = form.save(commit=False)
                # --- Génération automatique du matricule ---
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
                
                # Pa bezwen jere foto isit la - modèl la ap okipe sa otomatikman
                eleve.save()

                # --- Historique : nouvelle inscription ---
                HistoriqueEleve.objects.create(
                    eleve=eleve,
                    action='inscription',
                    description=f"Nouvelle inscription dans la classe {eleve.classe_actuelle}",
                    effectue_par=request.user
                )

                messages.success(request, f"L'élève {eleve.nom} {eleve.prenom} a été ajouté avec succès.")
                return redirect('eleves:eleve_list')

            except Exception as e:
                messages.error(request, f" Erreur lors de l'ajout : {str(e)}")
        else:
            messages.error(request, " Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = EleveForm()

    return render(request, 'add_eleves.html', {'form': form, 'classes': classes})


# -------------------- MODIFIER --------------------
# -------------------- MODIFIER --------------------
@role_required(['admin', 'directeur', 'secretaire'])
def eleve_update(request, pk):
    """Modifier les informations d'un élève"""
    eleve = get_object_or_404(Eleve, pk=pk)
    ancienne_classe = eleve.classe_actuelle
    
    # Jwenn lis klas aktif yo
    classes = Classe.objects.filter(statut='actif').order_by('nom_classe')

    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES, instance=eleve)
        if form.is_valid():
            eleve_modifie = form.save(commit=False)

            # --- Historique en cas de changement de classe ---
            if ancienne_classe != eleve_modifie.classe_actuelle:
                HistoriqueEleve.objects.create(
                    eleve=eleve,
                    action='changement_classe',
                    description=f"L'élève a été déplacé de {ancienne_classe} à {eleve_modifie.classe_actuelle}",
                    effectue_par=request.user
                )

            eleve_modifie.save()
            messages.success(request, "✅ Les informations de l'élève ont été mises à jour.")
            return redirect('eleves:eleve_list', pk=eleve.pk)
        else:
            messages.error(request, "Erreurs dans le formulaire.")
    else:
        form = EleveForm(instance=eleve)

    return render(request, 'eleve_update.html', {
        'form': form, 
        'eleve': eleve,
        'classes': classes  # Pase klas yo nan kontèks la
    })


# -------------------- ARCHIVER --------------------
@role_required(['admin', 'directeur', 'secretaire'])
def eleve_archiver(request, pk):
    """Archiver un élève"""
    eleve = get_object_or_404(Eleve, pk=pk)
    if eleve.statut == 'archive':
        messages.warning(request, " Cet élève est déjà archivé.")
    else:
        eleve.statut = 'archive'
        eleve.save()
        messages.success(request, f" L’élève {eleve.nom} {eleve.prenom} a été archivé.")
    return redirect('eleves:eleve_list')


# -------------------- RESTAURER --------------------
@role_required(['admin', 'directeur'])
def eleve_restaurer(request, pk):
    """Restaurer un élève archivé"""
    eleve = get_object_or_404(Eleve, pk=pk)
    if eleve.statut == 'archive':
        eleve.statut = 'actif'
        eleve.save()
        messages.success(request, f"✅ L’élève {eleve.nom} {eleve.prenom} a été restauré.")
    return redirect('eleves:eleve_list')


# -------------------- ARCHIVES --------------------
@login_required
def eleve_archives(request):
    """Liste des élèves archivés"""
    eleves_archives = Eleve.objects.filter(statut='archive')
    return render(request, 'eleve_archiver.html', {'eleves': eleves_archives})


# -------------------- SUPPRIMER --------------------
@role_required(['admin', 'directeur'])
def eleve_delete(request, pk):
    """Suppression définitive d’un élève"""
    eleve = get_object_or_404(Eleve, pk=pk)
    eleve.delete()
    messages.success(request, f" L’élève {eleve.nom} {eleve.prenom} a été supprimé définitivement.")
    return redirect('eleves:eleve_list')
