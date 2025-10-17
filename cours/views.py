from django.shortcuts import render

# Create your views here.
def cours(request):
    return render(request, 'cours/cours.html')   

def ajouter_cours(request):
    return render(request, 'cours/ajouter_cours.html')

def modifier_cours(request):
    return render(request, 'cours/modifier_cours.html')

def supprimer_cours(request):
    return render(request, 'cours/supprimer_cours.html')
