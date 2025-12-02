# annee_scolaire/views.py
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import AnneeScolaire

def changer_annee_actuelle(request, annee_id):
    if request.method == 'POST':
        annee = get_object_or_404(AnneeScolaire, id=annee_id)
        
        # Met tout lòt annee a "False"
        AnneeScolaire.objects.filter(est_actuelle=True).update(est_actuelle=False)
        
        # Aktive annee chwazi a
        annee.est_actuelle = True
        annee.save()
        
        messages.success(request, f"Année scolaire {annee.nom} est maintenant active")
    
    return redirect(request.META.get('HTTP_REFERER', 'accueil'))