from urllib import request
from django.shortcuts import render

# Create your views here.

def presence_list(request):
    # Logique pour récupérer et afficher la liste des présences
    return render(request, 'presences/presence_list.html')