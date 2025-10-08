
from . import views
from django.urls import path

app_name = 'evaluations'
urlpatterns = [
    path('evaluations/', views.evaluation_list, name='evaluation_list'),
    # Ajoutez d'autres chemins URL pour les évaluations si nécessaire
]