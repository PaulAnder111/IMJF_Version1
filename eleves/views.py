from django.shortcuts import render

# Create your views here.
def eleves(request):
    return render(request, 'eleves.html')
