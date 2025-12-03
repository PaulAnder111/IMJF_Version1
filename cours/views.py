from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cours, HistoriqueCours
from .forms import CoursForm
from matieres.models import Matiere
from classes.models import Classe
from enseignants.models import Enseignant
from annee_scolaire.models import AnneeScolaire  # SEUL IMPORT NÉCESSAIRE
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.template.loader import get_template
import io

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

from annee_scolaire.models import AnneeScolaire

import json
from django.utils.html import escape

def exporter_cours(request):
    try:
        annee_actuelle = AnneeScolaire.objects.get(est_annee_courante=True)
        cours_qs = Cours.objects.filter(annee_scolaire=annee_actuelle)
    except AnneeScolaire.DoesNotExist:
        annee_actuelle = None
        cours_qs = Cours.objects.all()

    # 🔥 Charger les relations pour éviter les requêtes multiples
    cours_qs = cours_qs.select_related('matiere', 'classe', 'enseignant')

    # 🔥 CORRIGÉ: Utiliser les bons noms d'attributs
    cours_list = []
    for c in cours_qs:
        matiere_nom = c.matiere.nom_matiere if c.matiere else "Non spécifié"
        classe_nom = c.classe.nom_classe if c.classe else "Non affecté"
        enseignant_nom = f"{c.enseignant.nom} {c.enseignant.prenom}" if c.enseignant else "Non attribué"
        
        cours_list.append({
            'matiere': escape(matiere_nom),
            'classe': escape(classe_nom),
            'enseignant': escape(enseignant_nom),
            'jour': c.jour,
            'heures': f"{c.heure_debut} → {c.heure_fin}",
            'salle': c.salle or "—",
            'statut': c.get_statut_display() or c.statut
        })

    total_count = len(cours_list)
    # 🔥 CORRIGÉ: Statuts valides selon votre modèle Cours
    actif_count = sum(1 for c in cours_list if c['statut'].lower() in ['planifié', 'en cours'])
    inactif_count = total_count - actif_count
    enseignant_count = len(set(c['enseignant'] for c in cours_list if c['enseignant'] != "Non attribué"))

    return render(request, 'cours/exporter_cours.html', {
        'cours_json': json.dumps(cours_list),
        'cours': cours_qs,
        'annee_actuelle': annee_actuelle,
        'total_count': total_count,
        'actif_count': actif_count,
        'inactif_count': inactif_count,
        'enseignant_count': enseignant_count,
    })
#==================LISTE COURS==================#
#==============================================#
@login_required
def cours_list(request):
    cours = Cours.objects.select_related('matiere', 'classe', 'enseignant').order_by('-id')
    total_cours = Cours.objects.count()
    cours_actifs = Cours.objects.filter(statut='actif').count()
    cours_inactifs = Cours.objects.filter(statut='inactif').count()
    total_enseignants = Enseignant.objects.filter(statut='actif').count()
    classes = Classe.objects.all()
    return render(request, 'cours/cours.html', {
        'cours': cours,
        'total_cours': total_cours,
        'cours_actifs': cours_actifs,
        'cours_inactifs': cours_inactifs,
        'total_enseignants': total_enseignants,
        'classes': classes,
    })

#==================CREATE COURS==================#
#==============================================#

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from utilisateurs.decorators import role_required

@role_required(['admin', 'directeur'])
def cours_create(request):
    # Récupère l'année active - UTILISE LA MÉTHODE DE CLASSE
    annee_active = AnneeScolaire.get_annee_courante()
    
    if request.method == 'POST':
        try:
            matiere_id = request.POST.get('matiere')
            classe_id = request.POST.get('classe')
            enseignant_id = request.POST.get('enseignant')
            jour = request.POST.get('jour')
            heure_debut = request.POST.get('heure_debut')
            heure_fin = request.POST.get('heure_fin')
            salle = request.POST.get('salle', '')
            statut = request.POST.get('statut') or 'planifie'
            annee_scolaire_id = request.POST.get('annee_scolaire')
            
            # Validation de l'année scolaire
            if annee_scolaire_id:
                annee_scolaire = AnneeScolaire.objects.get(id=annee_scolaire_id)
            else:
                # Si pas d'année spécifiée, utiliser l'année active
                annee_scolaire = annee_active

            cours = Cours(
                matiere_id=matiere_id,
                classe_id=classe_id,
                enseignant_id=enseignant_id,
                jour=jour,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                salle=salle,
                statut=statut,
                annee_scolaire=annee_scolaire,
                cree_par=request.user
            )

            cours.save()

            # 🔹 Enregistrement dans l'historique
            HistoriqueCours.objects.create(
                cours=cours,
                action="Création",
                user=request.user,
                description=f"Cours créé pour {cours.classe} avec {cours.enseignant}"
            )

            messages.success(request, "✅ Le cours a été ajouté avec succès !")
            return redirect('cours:cours')

        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for err in errors:
                    messages.error(request, f"⚠️ {err}")
        except Exception as e:
            messages.error(request, f"❌ Erreur inattendue : {str(e)}")

    # 🔹 Récupérer les données nécessaires pour les listes déroulantes
    matieres = Matiere.objects.all()
    classes = Classe.objects.all()
    enseignants = Enseignant.objects.all()
    
    # 🔹 Récupérer les années scolaires depuis la base de données
    annees_scolaires = AnneeScolaire.objects.all().order_by('-date_debut')

    # 🔹 Récupérer les options depuis le modèle
    jours = Cours.JOURS
    statuts = Cours.STATUTS_COURS

    return render(request, 'cours/ajouter_cours.html', {
        'matieres': matieres,
        'classes': classes,
        'enseignants': enseignants,
        'jours': jours,
        'statuts': statuts,
        'annees_scolaires': annees_scolaires,
        'annee_active': annee_active,
    })

#==================UPDATE COURS==================#
#==============================================#

@role_required(['admin', 'directeur'])
def cours_update(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    matieres = Matiere.objects.all()
    classes = Classe.objects.all()
    enseignants = Enseignant.objects.all()
    annees_scolaires = AnneeScolaire.objects.all().order_by('-date_debut')

    if request.method == "POST":
        matiere_id = request.POST.get("matiere")
        classe_id = request.POST.get("classe")
        enseignant_id = request.POST.get("enseignant")
        jour = request.POST.get("jour")
        heure_debut = request.POST.get("heure_debut")
        heure_fin = request.POST.get("heure_fin")
        salle = request.POST.get("salle")
        statut = request.POST.get("statut", "inactif")
        annee_scolaire_id = request.POST.get("annee_scolaire")

        conflit = Cours.objects.filter(
            enseignant_id=enseignant_id,
            jour=jour,
            heure_debut__lt=heure_fin,
            heure_fin__gt=heure_debut
        ).exclude(id=cours.id).exists()

        if conflit:
            messages.error(
                request,
                "⚠️ Attention ! Ce professeur a déjà un cours à ce créneau."
            )
        else:
            cours.matiere_id = matiere_id
            cours.classe_id = classe_id
            cours.enseignant_id = enseignant_id
            cours.jour = jour
            cours.heure_debut = heure_debut
            cours.heure_fin = heure_fin
            cours.salle = salle
            cours.statut = statut
            
            # Mettre à jour l'année scolaire
            if annee_scolaire_id:
                cours.annee_scolaire_id = annee_scolaire_id
            
            cours.modifier_par = request.user
            cours.save()

            HistoriqueCours.objects.create(
                cours=cours,
                action="Modification",
                user=request.user,
                description=f"Cours modifié pour {cours.classe} avec {cours.enseignant}"
            )

            messages.success(request, "✅ Le cours a été mis à jour avec succès !")
            return redirect('cours:cours')

    return render(request, 'cours/modifier_cours.html', {
        'cours': cours,
        'matieres': matieres,
        'classes': classes,
        'enseignants': enseignants,
        'jours': JOURS,
        'annees_scolaires': annees_scolaires,
        'annee_active': AnneeScolaire.get_annee_courante(),
    })

#==================DELETE COURS==================#
#==============================================#

@role_required(['admin', 'directeur'])
def cours_delete(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    if request.method == 'POST':
        HistoriqueCours.objects.create(
            cours=cours,
            action="Suppression",
            user=request.user,
            description=f"Cours supprimé pour {cours.classe} avec {cours.enseignant}"
        )
        cours.delete()
        messages.success(request, "Cours supprimé avec succès ❌")
        return redirect('cours:cours')
    return render(request, 'cours/cours_confirm_delete.html', {'cours': cours})

#==================DETAIL COURS==================#
@login_required
def cours_detail(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    return render(request, 'cours/cours_detail.html', {'cours': cours})
#==============================================#
