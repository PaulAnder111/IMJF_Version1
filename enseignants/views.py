from django.shortcuts import render

# Create your views here.
def enseignants(request):
    return render(request, 'enseignants/enseignants.html')