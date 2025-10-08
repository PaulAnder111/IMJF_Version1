from django.shortcuts import render

# Create your views here.

def classes(request):
    return render(request, 'classes/classes.html')
