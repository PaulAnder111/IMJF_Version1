from django.urls import path
from . import views

app_name = 'enseignants'

urlpatterns = [
    path('enseignants', views.enseignants, name='enseignants'),
    path('ajouter_enseignant', views.ajouter_enseignants, name='ajouter_enseignant'),
    path('modifier_enseignants', views.modifier_enseignants, name='modifier_enseignant'),
]