from django.shortcuts import render

# Create your views here.
def note_list(request):
    # Logique pour récupérer et afficher la liste des notes
    return render(request, 'notes/notes_list.html')
    