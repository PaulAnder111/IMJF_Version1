from . import views
from django.urls import path

app_name = 'matieres'

urlpatterns = [
    path('matieres/', views.matieres, name='matieres'),
    # Ajoutez d'autres chemins URL pour les matières si nécessaire
    path('ajouter_matiere/', views.ajouter_matiere, name='ajouter_matiere'),
    path('modifier_matiere/<int:matiere_id>/', views.modifier_matiere, name='modifier_matiere'),
]