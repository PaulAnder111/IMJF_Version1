from django.shortcuts import render

# Create your views here.
def eleves(request):
    return render(request, 'eleves.html')

def add_eleves(request):
    return render(request, 'add_eleves.html')

def modifier_eleves(request):
    return render(request, 'modifier_eleves.html')
