from django.urls import path
from . import views

app_name = 'cours'

urlpatterns = [
    # Cours
    path('cours/', views.cours, name='cours'),
    path('ajouter_cours/', views.ajouter_cours, name='ajouter_cours'),
    path('modifier_cours/', views.modifier_cours, name='modifier_cours'),
]