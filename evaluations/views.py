from django.shortcuts import render

# Create your views here.
def evaluation_list(request):
    # Logique pour récupérer et afficher la liste des évaluations
    return render(request, 'evaluations/evaluation_list.html')
