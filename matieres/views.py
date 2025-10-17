from django.shortcuts import render

# Create your views here.

def matieres(request):
    # Logique pour récupérer et afficher la liste des matières
    return render(request, 'matieres/matieres.html')

def ajouter_matiere(request):
    # Logique pour ajouter une nouvelle matière
    return render(request, 'matieres/ajouter_matiere.html')

def modifier_matiere(request, matiere_id):
    # Logique pour modifier une matière existante
    return render(request, 'matieres/modifier_matiere.html', {'matiere_id': matiere_id})