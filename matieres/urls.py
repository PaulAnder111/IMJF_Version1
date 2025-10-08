from . import views
from django.urls import path

app_name = 'matieres'

urlpatterns = [
    path('matieres/', views.matieres, name='matieres'),
    # Ajoutez d'autres chemins URL pour les matières si nécessaire
]