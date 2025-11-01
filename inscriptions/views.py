from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Inscription, HistoriqueClasses
from .forms import InscriptionForm
from classes.models import Classe
from eleves.models import Eleve

# --- Fonksyon pou jenere Matricule otomatik ---
def generer_matricule():
    dernier = Eleve.objects.order_by('-id').first()
    num = 1
    if dernier and dernier.matricule:
        try:
            parts = dernier.matricule.split('-')
            if len(parts) >= 2:
                num = int(parts[-1]) + 1
        except (ValueError, IndexError):
            pass
    return f"ELEVE-{num:04d}"

# --- Fonksyon pou verifye wòl ---
def check_access(user):
    """Retounen True si user gen aksè CRUD sou enskripsyon."""
    return user.is_authenticated and (user.role in ['admin', 'directeur', 'secretaire'])

# --- CREATE ---
@login_required
def inscription_create(request):
    if not check_access(request.user):
        raise Http404("Page non trouvée.")

    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            # Verifikasyon: elèv pa ka nan plizyè klas menm ane a
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            date_naissance = form.cleaned_data['date_naissance']
            annee_scolaire = form.cleaned_data['annee_scolaire']
            if Inscription.objects.filter(
                nom=nom,
                prenom=prenom,
                date_naissance=date_naissance,
                annee_scolaire=annee_scolaire
            ).exists():
                messages.error(request, "Cet élève est déjà inscrit pour cette année scolaire.")
                return redirect('inscriptions:create_inscription')

            inscription = form.save(commit=False)
            inscription.cree_par = request.user
            inscription.statut = 'pre-inscrit'
            inscription.save()
            messages.success(request, f"Inscription de {inscription.prenom} {inscription.nom} créée avec succès.")
            return redirect('inscriptions:inscription_list')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = InscriptionForm()

    return render(request, 'inscriptions/create_inscription.html', {
        'form': form,
        'classes': Classe.objects.filter(statut='actif'),
    })

# --- LIST ---
@login_required
def inscription_list(request):
    inscriptions = Inscription.objects.all().order_by('-date_created')
    return render(request, 'inscriptions/inscription_list.html', {'inscriptions': inscriptions})

# --- DETAIL ---
@login_required
def inscription_detail(request, pk):
    inscription = get_object_or_404(Inscription, pk=pk)
    return render(request, 'inscriptions/afficher_inscription.html', {'inscription': inscription})

# --- UPDATE ---
@login_required
def inscription_update(request, pk):
    inscription = get_object_or_404(Inscription, pk=pk)
    if not check_access(request.user):
        raise Http404("Page non trouvée.")

    if request.method == 'POST':
        form = InscriptionForm(request.POST, instance=inscription)
        if form.is_valid():
            # Validasyon menm ane
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            date_naissance = form.cleaned_data['date_naissance']
            annee_scolaire = form.cleaned_data['annee_scolaire']
            if Inscription.objects.filter(
                nom=nom,
                prenom=prenom,
                date_naissance=date_naissance,
                annee_scolaire=annee_scolaire
            ).exclude(pk=inscription.pk).exists():
                messages.error(request, "Cet élève est déjà inscrit pour cette année scolaire.")
                return redirect('inscriptions:updates_inscriptions', pk=inscription.pk)

            inscription = form.save()

            # Si validé oswa aktif, kreye Eleve otomatikman
            if inscription.statut in ['validé', 'aktif'] and not inscription.eleve:
                matricule = generer_matricule()
                eleve = Eleve.objects.create(
                    matricule=matricule,
                    nom=inscription.nom,
                    prenom=inscription.prenom,
                    date_naissance=inscription.date_naissance,
                    lieu_naissance=inscription.lieu_naissance,
                    sexe=inscription.sexe,
                    adresse=inscription.adresse,
                    niveau=inscription.niveau,
                    classe_actuelle=inscription.classe,
                    statut='actif'
                )
                inscription.eleve = eleve
                inscription.save()

                # Ajoute nan historique otomatik
                HistoriqueClasses.objects.create(
                    eleve=eleve,
                    classe=inscription.classe,
                    annee_scolaire=inscription.annee_scolaire
                )

            messages.success(request, "Inscription mise à jour avec succès !")
            return redirect('inscriptions:afficher_inscription', pk=inscription.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = InscriptionForm(instance=inscription)

    return render(request, 'inscriptions/updates_inscriptions.html', {
        'form': form,
        'classes': Classe.objects.filter(statut='actif'),
        'inscription': inscription
    })

# --- DELETE ---
@login_required
def inscription_delete(request, pk):
    inscription = get_object_or_404(Inscription, pk=pk)
    if not check_access(request.user):
        raise Http404("Page non trouvée.")

    if request.method == 'POST':
        inscription.delete()
        messages.success(request, "Inscription supprimée avec succès.")
        return redirect('inscriptions:inscription_list')

    return redirect('inscriptions:afficher_inscription', pk=pk)

# --- VALIDER ---
@login_required
def inscription_valider(request, pk):
    if not check_access(request.user):
        raise Http404("Page non trouvée.")

    inscription = get_object_or_404(Inscription, pk=pk)

    if inscription.statut != 'pre-inscrit':
        messages.warning(request, "Cette inscription ne peut pas être validée.")
        return redirect('inscriptions:inscription_list')

    klas = inscription.classe
    if hasattr(klas, 'capacite_max') and klas.eleves_actuels.count() >= klas.capacite_max:
        messages.error(request, f"La classe {klas} est pleine !")
        return redirect('inscriptions:inscription_list')

    matricule = generer_matricule()
    eleve = Eleve.objects.create(
        matricule=matricule,
        nom=inscription.nom,
        prenom=inscription.prenom,
        date_naissance=inscription.date_naissance,
        lieu_naissance=inscription.lieu_naissance,
        sexe=inscription.sexe,
        adresse=inscription.adresse,
        niveau=inscription.niveau,
        classe_actuelle=klas,
        statut='actif'
    )

    inscription.eleve = eleve
    inscription.statut = 'aktif'
    inscription.save()

    # Mete istorik otomatik
    HistoriqueClasses.objects.create(
        eleve=eleve,
        classe=klas,
        annee_scolaire=inscription.annee_scolaire
    )

    messages.success(request, f"Inscription validée ! Élève {matricule} créé.")
    return redirect('inscriptions:inscription_list')
