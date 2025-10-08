from django.shortcuts import render

# Create your views here.

def matieres(request):
    # Logique pour récupérer et afficher la liste des matières
    return render(request, 'matieres/matieres.html')