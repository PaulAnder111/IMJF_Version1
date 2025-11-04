from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cours, HistoriqueCours
from .forms import CoursForm
from matieres.models import Matiere
from classes.models import Classe
from enseignants.models import Enseignant
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Cours
from django.template.loader import get_template
import io

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

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

@login_required
def cours_create(request):
    if request.method == 'POST':
        try:
            matiere_id = request.POST.get('matiere')
            classe_id = request.POST.get('classe')
            enseignant_id = request.POST.get('enseignant')
            jour = request.POST.get('jour')
            heure_debut = request.POST.get('heure_debut')
            heure_fin = request.POST.get('heure_fin')
            salle = request.POST.get('salle', '')
            statut = 'actif' if request.POST.get('statut') == 'actif' else 'inactif'

            cours = Cours(
                matiere_id=matiere_id,
                classe_id=classe_id,
                enseignant_id=enseignant_id,
                jour=jour,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                salle=salle,
                statut=statut,
                cree_par=request.user
            )

            cours.save()

            # 🔹 Enregistrement de l'historique
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

    matieres = Matiere.objects.all()
    classes = Classe.objects.all()
    enseignants = Enseignant.objects.all()
    return render(request, 'cours/ajouter_cours.html', {
        'matieres': matieres,
        'classes': classes,
        'enseignants': enseignants
    })


@login_required
def cours_update(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    matieres = Matiere.objects.all()
    classes = Classe.objects.all()
    enseignants = Enseignant.objects.all()

    if request.method == "POST":
        matiere_id = request.POST.get("matiere")
        classe_id = request.POST.get("classe")
        enseignant_id = request.POST.get("enseignant")
        jour = request.POST.get("jour")
        heure_debut = request.POST.get("heure_debut")
        heure_fin = request.POST.get("heure_fin")
        salle = request.POST.get("salle")
        statut = request.POST.get("statut", "inactif")

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
    })


@login_required
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
