from django.shortcuts import render

# Create your views here.

def classes(request):
    return render(request, 'classes/classes.html')

def ajouter_classes(request):
    return render(request, 'classes/ajouter_classes.html')

def modifier_classes(request):
    return render(request, 'classes/modifier_classes.html')
