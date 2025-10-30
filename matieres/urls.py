# matieres/urls.py

from django.urls import path
from . import views

app_name = 'matieres'

urlpatterns = [
    path('matieres/', views.matiere_list, name='matieres'),
    path('ajouter_matiere/', views.matiere_create, name='ajouter_matiere'),
    path('modifier_modifier/<int:pk>/', views.matiere_update, name='modifier_matiere'),
    path('supprimer/<int:pk>/', views.matiere_delete, name='matiere_delete'),
]