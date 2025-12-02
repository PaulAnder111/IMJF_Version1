# annee_scolaire/view_mixins.py
from .models import AnneeScolaire

class FiltreAnneeScolaireMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.model, 'annee_scolaire'):
            try:
                annee_actuelle = AnneeScolaire.objects.get(est_actuelle=True)
                return queryset.filter(annee_scolaire=annee_actuelle)
            except AnneeScolaire.DoesNotExist:
                return queryset
        return queryset