# matieres/views.py
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Matiere
from django.db.models import Q, Sum
from .forms import MatiereForm

# def is_secretaire_or_directeur(user):
#     return user.role in ['secretaire', 'directeur']

@login_required
def matiere_list(request):
    # 🔍 Rechèch
    search = request.GET.get('search')
    matieres = Matiere.objects.all()

    if search:
        matieres = matieres.filter(
            Q(nom_matiere__icontains=search) |
            Q(code_matiere__icontains=search)
        )

    # 🧮 Estatistik
    total_matieres = Matiere.objects.count()
    matieres_actives = Matiere.objects.filter(statut='actif').count()
    matieres_inactives = Matiere.objects.filter(statut='inactif').count()
    total_heures = Matiere.objects.aggregate(total=Sum('heure_hebdomadaire'))['total'] or 0

    return render(request, 'matieres/matieres.html', {
        'matieres': matieres,
        'total_matieres': total_matieres,
        'matieres_actives': matieres_actives,
        'matieres_inactives': matieres_inactives,
        'total_heures': total_heures,
    })

@login_required
def matiere_create(request):
    if request.method == 'POST':
        form = MatiereForm(request.POST)
        if form.is_valid():
            matiere = form.save(commit=False)
            if not matiere.statut:
                matiere.statut = 'actif'
            matiere.save()
            messages.success(request, "Matière enregistrée avec succès !")
            return redirect('matieres:matieres')
        else:
            messages.error(request, "Erreur lors de l’enregistrement.")
    else:
        form = MatiereForm()
    return render(request, 'matieres/ajouter_matiere.html', {'form': form, 'titre': "Ajouter une matière"})

@login_required
def matiere_update(request, pk):
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        form = MatiereForm(request.POST, instance=matiere)
        if form.is_valid():
            form.save()
            return redirect('matieres:matieres')
    else:
        form = MatiereForm(instance=matiere)
    return render(request, 'matieres/modifier_matiere.html', {'form': form, 'titre': "Modifier une matière"})

@login_required
def matiere_delete(request, pk):
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        # Verifye si matyè a itilize nan yon kou
        if matiere.cours_set.exists():
            messages.error(request, "Impossible de supprimer cette matière car elle est utilisée dans des cours.")
        else:
            matiere.delete()
            messages.success(request, "Matière supprimée avec succès !")
        return redirect('matieres:matieres')
    return render(request, 'matieres/matiere_confirm_delete.html', {'matiere': matiere})