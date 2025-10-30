# cours/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from .models import Cours
from .forms import CoursForm

# def is_directeur(user):
#     return user.role == 'directeur'

login_required
def cours_list(request):
    cours = Cours.objects.select_related('matiere', 'classe', 'enseignant').all()
    return render(request, 'cours/cours.html', {'cours': cours})

login_required
def cours_create(request):
    if request.method == 'POST':
        form = CoursForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cours:cours')
    else:
        form = CoursForm()
    return render(request, 'cours/ajouter_cours.html', {'form': form, 'titre': "Ajouter un cours"})

login_required
def cours_update(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    if request.method == 'POST':
        form = CoursForm(request.POST, instance=cours)
        if form.is_valid():
            form.save()
            return redirect('cours:cours')
    else:
        form = CoursForm(instance=cours)
    return render(request, 'cours/modifier_cours.html', {'form': form, 'titre': "Modifier un cours"})

login_required
def cours_delete(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    if request.method == 'POST':
        cours.delete()
        return redirect('cours:cours')
    return render(request, 'cours/cours_confirm_delete.html', {'cours': cours})