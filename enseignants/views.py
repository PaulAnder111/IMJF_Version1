from django.shortcuts import render

# Create your views here.
def enseignants(request):
    return render(request, 'enseignants/enseignants.html')


def ajouter_enseignants(request):
    return render(request, 'enseignants/ajouter_enseignant.html')


def modifier_enseignants(request):
    return render(request, 'enseignants/modifier_enseignant.html')