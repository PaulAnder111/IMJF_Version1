from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from eleves.models import Eleve

from utilisateurs.decorators import role_required
from .models import Classe
from django.db.models import Avg
from .forms import ClasseForm

@login_required
def classe_list(request):
    classes_qs = Classe.objects.all().order_by('niveau', 'nom_classe')

    # Rechèch ak filtre
    search = request.GET.get('search')
    niveau = request.GET.get('niveau')
    statut = request.GET.get('statut')

    if search:
        classes_qs = classes_qs.filter(nom_classe__icontains=search)
    if niveau:
        classes_qs = classes_qs.filter(niveau=niveau)
    if statut:
        classes_qs = classes_qs.filter(statut=statut)

    # Statistik (sèlman sou tout klas yo, pa sèlman filtred yo)
    total_classes = Classe.objects.count()
    classes_actives = Classe.objects.filter(statut='actif').count()
    total_eleves = Eleve.objects.filter(statut='actif').count()  # oswa .count() si ou vle tout eleve
    capacite_moyenne = Classe.objects.aggregate(avg=Avg('capacite_max'))['avg'] or 0

    # Pagination pou lis la
    from django.core.paginator import Paginator
    paginator = Paginator(classes_qs, 5)  # 10 klas pa paj
    page_number = request.GET.get('page')
    classes = paginator.get_page(page_number)

    context = {
        'classes': classes,
        'total_classes': total_classes,
        'classes_actives': classes_actives,
        'total_eleves': total_eleves,
        'capacite_moyenne': capacite_moyenne,
    }
    return render(request, 'classes/classe_list.html', context)

@role_required(['admin', 'directeur'])
def classe_create(request):
    if request.method == 'POST':
        form = ClasseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Classe créée avec succès !")
            return redirect('classes:classe_list')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ClasseForm()
    return render(request, 'classes/ajouter_classes.html', {'form': form})

@role_required(['admin', 'directeur'])
def classe_update(request, pk):
    classe = get_object_or_404(Classe, pk=pk)
    if request.method == 'POST':
        form = ClasseForm(request.POST, instance=classe)
        if form.is_valid():
            form.save()
            messages.success(request, "Classe mise à jour avec succès !")
            return redirect('classes:classe_list')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ClasseForm(instance=classe)
    return render(request, 'classes/modifier_classes.html', {'form': form, 'classe': classe})

@role_required(['admin', 'directeur'])
def classe_delete(request, pk):
    classe = get_object_or_404(Classe, pk=pk)
    if request.method == 'POST':
        classe.delete()
        messages.success(request, "Classe supprimée avec succès !")
        return redirect('classes:classe_list')
    return render(request, 'classes/classe_confirm_delete.html', {'classe': classe})
