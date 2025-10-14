from django.shortcuts import render

def inscription(request):
    return render(request, 'inscriptions/inscription_list.html')       


def create_inscrip(request):
    return render(request, 'inscriptions/create_inscriptions.html')
