from django.shortcuts import render

def inscription(request):
    return render(request, 'inscriptions/inscription_list.html')       


def create_inscription(request):
    return render(request, 'inscriptions/create_inscription.html')

def updates_inscriptions(request):
    return render(request, 'inscriptions/updates_inscriptions.html')

def delete_inscription(request):
    return render(request, 'inscriptions/delete_inscription.html')
