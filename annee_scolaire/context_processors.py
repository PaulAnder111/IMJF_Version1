from .models import AnneeScolaire

def annee_scolaire_actuelle(request):
    try:
        # KORIKSYON: Chanje 'est_actuelle' pou 'est_annee_courante'
        annee_actuelle = AnneeScolaire.objects.get(est_annee_courante=True)
        return {'annee_actuelle': annee_actuelle}
    except AnneeScolaire.DoesNotExist:
        return {'annee_actuelle': None}