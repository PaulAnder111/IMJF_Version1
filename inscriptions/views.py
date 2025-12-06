from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from utilisateurs.decorators import role_required
from django.contrib.auth.models import User
from enseignants.models import Enseignant
from matieres.models import Matiere
from .models import Inscription, HistoriqueClasses
from .forms import InscriptionForm
from classes.models import Classe
from eleves.models import Eleve
from django.urls import reverse
from utilisateurs.models import Notification


@login_required
def dash_admin(request):
    # Statistiques principales
    inscriptions_count = Inscription.objects.count()
    eleves_count = Eleve.objects.count()
    enseignants_count = Enseignant.objects.count()
    classes_count = Classe.objects.count()
    matieres_count = Matiere.objects.count()
    users_count = User.objects.count()
    secretaires_count = User.objects.filter(role='secretaire').count()
    directeurs_count = User.objects.filter(role='directeur').count()
    archives_count = 0  # Si w gen modèl archive, mete li la
    cours_count = 0     # Si w gen modèl Cours, mete li la

    # Nouvelles inscriptions (5 dernières)
    recent_inscriptions = Inscription.objects.all().order_by('-date_created')[:5]

    context = {
        'inscriptions_count': inscriptions_count,
        'eleves_count': eleves_count,
        'enseignants_count': enseignants_count,
        'classes_count': classes_count,
        'matieres_count': matieres_count,
        'users_count': users_count,
        'secretaires_count': secretaires_count,
        'directeurs_count': directeurs_count,
        'archives_count': archives_count,
        'cours_count': cours_count,
        'recent_inscriptions': recent_inscriptions,
    }

    return render(request, 'utilisateurs/dash_admin.html', context)

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
    return user.is_authenticated and (user.role in ['admin', 'directeur', 'secretaire', 'archives'])
    

# --- CREATE ---
#------------------------------
@role_required(['admin', 'directeur', 'secretaire'])
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

            # If an Eleve record already exists for this person, ensure they are not
            # already assigned to a different class for the same school year.
            try:
                eleve_qs = Eleve.objects.filter(
                    nom__iexact=nom.strip(),
                    prenom__iexact=prenom.strip(),
                    date_naissance=date_naissance
                )
                if eleve_qs.exists():
                    eleve = eleve_qs.first()
                    if HistoriqueClasses.objects.filter(eleve=eleve, annee_scolaire=annee_scolaire).exclude(classe=form.cleaned_data.get('classe')).exists():
                        messages.error(request, "Cet élève est déjà assigné à une autre classe pour cette année scolaire.")
                        return redirect('inscriptions:create_inscription')
            except Exception:
                # if Eleve or HistoriqueClasses not available just continue
                pass

            # Also ensure the person is not already registered as an Enseignant
            try:
                if Enseignant.objects.filter(
                    nom__iexact=nom.strip(),
                    prenom__iexact=prenom.strip(),
                    date_naissance=date_naissance
                ).exists():
                    messages.error(request, "Impossible d'enregistrer : cette personne est déjà enregistrée comme enseignant.")
                    return redirect('inscriptions:create_inscription')
            except Exception:
                pass

            inscription = form.save(commit=False)
            inscription.cree_par = request.user

            # Si kreye pa admin oswa directeur, valide otomatikman
            if request.user.role in ['admin', 'directeur']:
                inscription.statut = 'actif'
            else:
                inscription.statut = 'pre-inscrit'

            inscription.save()
            # Si inscription valide otomatikman (eg. kreye pa admin/directeur), kreye Eleve imedyatman
            if inscription.statut == 'actif' and not inscription.eleve:
                try:
                    # verifye pa yon enseignant
                    if Enseignant.objects.filter(
                        nom__iexact=inscription.nom.strip(),
                        prenom__iexact=inscription.prenom.strip(),
                        date_naissance=inscription.date_naissance
                    ).exists():
                        messages.error(request, "Impossible d'enregistrer l'élève : cette personne est déjà enregistrée comme enseignant.")
                    else:
                        # Check existing Eleve across all objects (including archived)
                        existing = Eleve.all_objects.filter(
                            nom__iexact=inscription.nom.strip(),
                            prenom__iexact=inscription.prenom.strip(),
                            date_naissance=inscription.date_naissance
                        ).first()
                        if existing:
                            # If the student already has a history for this year, abort
                            if HistoriqueClasses.objects.filter(eleve=existing, annee_scolaire=inscription.annee_scolaire).exists():
                                messages.error(request, "Cet élève est déjà inscrit pour cette année scolaire.")
                                # do not proceed to create or link
                            else:
                                # If archived, restore status via update to avoid validations
                                if getattr(existing, 'statut', None) == 'radié':
                                    Eleve.all_objects.filter(pk=existing.pk).update(statut='actif')
                                # Update classe_actuelle and other fields via update to avoid full_clean
                                Eleve.all_objects.filter(pk=existing.pk).update(
                                    classe_actuelle=inscription.classe,
                                    niveau=inscription.niveau,
                                    adresse=inscription.adresse
                                )
                                # Link inscription to existing eleve and create history
                                inscription.eleve = existing
                                inscription.statut = 'actif'
                                inscription.save()
                                HistoriqueClasses.objects.create(
                                    eleve=existing,
                                    classe=inscription.classe,
                                    annee_scolaire=inscription.annee_scolaire
                                )
                        else:
                            # Create new Eleve
                            matricule = generer_matricule()
                            try:
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
                                HistoriqueClasses.objects.create(
                                    eleve=eleve,
                                    classe=inscription.classe,
                                    annee_scolaire=inscription.annee_scolaire
                                )
                            except Exception:
                                messages.error(request, "Erreur lors de la création de l'élève. Vérifiez les doublons ou les données.")
                except Exception:
                    # log or notify, but don't crash the flow
                    pass
            # Create notifications for admin and directeur so they can validate
            try:
                target_url = reverse('inscriptions:afficher_inscription', args=[inscription.pk])
            except Exception:
                target_url = '#'

            title = f"Nouvelle inscription: {inscription.prenom} {inscription.nom}"
            message = f"Inscription pré-enregistrée par {request.user.get_full_name() or request.user.username}."
            for role in ['admin', 'directeur']:
                Notification.objects.create(
                    recipient_role=role,
                    type='inscription',
                    title=title,
                    message=message,
                    target_url=target_url,
                )
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
    inscriptions = Inscription.objects.select_related('classe', 'eleve', 'cree_par').all().order_by('-date_created')
    return render(request, 'inscriptions/inscription_list.html', {'inscriptions': inscriptions})

# --- DETAIL ---
@login_required
def inscription_detail(request, pk):
    inscription = get_object_or_404(Inscription.objects.select_related('classe', 'eleve', 'cree_par'), pk=pk)
    return render(request, 'inscriptions/afficher_inscription.html', {'inscription': inscription})

# --- UPDATE ---
@role_required(['admin', 'directeur', 'secretaire'])
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
            if inscription.statut in ['validé', 'actif'] and not inscription.eleve:
                # Before creating Eleve, ensure this person is not registered as an Enseignant
                try:
                    if Enseignant.objects.filter(
                        nom__iexact=inscription.nom.strip(),
                        prenom__iexact=inscription.prenom.strip(),
                        date_naissance=inscription.date_naissance
                    ).exists():
                        messages.error(request, "Impossible de créer l'élève : cette personne est enregistrée comme enseignant.")
                        return redirect('inscriptions:updates_inscriptions', pk=inscription.pk)
                except Exception:
                    pass

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
@role_required(['admin', 'directeur'])
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
@role_required(['admin', 'directeur'])
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

    # Before creating Eleve, ensure this person is not registered as an Enseignant
    try:
        if Enseignant.objects.filter(
            nom__iexact=inscription.nom.strip(),
            prenom__iexact=inscription.prenom.strip(),
            date_naissance=inscription.date_naissance
        ).exists():
            messages.error(request, "Impossible de valider l'inscription : cette personne est enregistrée comme enseignant.")
            return redirect('inscriptions:inscription_list')

        # Also ensure they are not already assigned to a class this year
        eleve_qs = Eleve.objects.filter(
            nom__iexact=inscription.nom.strip(),
            prenom__iexact=inscription.prenom.strip(),
            date_naissance=inscription.date_naissance
        )
        if eleve_qs.exists():
            eleve_check = eleve_qs.first()
            if HistoriqueClasses.objects.filter(eleve=eleve_check, annee_scolaire=inscription.annee_scolaire).exists():
                messages.error(request, "Cet élève est déjà inscrit pour cette année scolaire.")
                return redirect('inscriptions:inscription_list')
    except Exception:
        pass

    matricule = generer_matricule()
    # Attempt to find existing Eleve (including archived)
    existing = Eleve.all_objects.filter(
        nom__iexact=inscription.nom.strip(),
        prenom__iexact=inscription.prenom.strip(),
        date_naissance=inscription.date_naissance
    ).first()

    if existing:
        # If already has history for this year, block
        if HistoriqueClasses.objects.filter(eleve=existing, annee_scolaire=inscription.annee_scolaire).exists():
            messages.error(request, "Cet élève est déjà inscrit pour cette année scolaire.")
            return redirect('inscriptions:inscription_list')

        # Restore if archived
        if existing.statut == 'radié':
            Eleve.all_objects.filter(pk=existing.pk).update(statut='actif')

        # Update class and other details via update()
        Eleve.all_objects.filter(pk=existing.pk).update(
            classe_actuelle=klas,
            niveau=inscription.niveau,
            adresse=inscription.adresse
        )

        inscription.eleve = existing
        inscription.statut = 'actif'
        inscription.save()

        # Mete istorik otomatik
        HistoriqueClasses.objects.create(
            eleve=existing,
            classe=klas,
            annee_scolaire=inscription.annee_scolaire
        )

        messages.success(request, f"Inscription validée ! Élève lié (ID {existing.pk}) réutilisé.")
        return redirect('inscriptions:inscription_list')

    # No existing Eleve, create a new one
    try:
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
        inscription.statut = 'actif'
        inscription.save()

        # Mete istorik otomatik
        HistoriqueClasses.objects.create(
            eleve=eleve,
            classe=klas,
            annee_scolaire=inscription.annee_scolaire
        )

        messages.success(request, f"Inscription validée ! Élève {matricule} créé.")
        return redirect('inscriptions:inscription_list')
    except Exception:
        messages.error(request, "Erreur lors de la création de l'élève. Vérifiez les doublons ou les données.")
        return redirect('inscriptions:inscription_list')
