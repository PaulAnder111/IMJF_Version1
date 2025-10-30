# cours/urls.py

from django.urls import path
from . import views

app_name = 'cours'

urlpatterns = [
    path('', views.cours_list, name='cours'),
    path('ajouter/', views.cours_create, name='ajouter_cours'),
    path('modifier/<int:pk>/', views.cours_update, name='modifier_cours'),
    path('supprimer/<int:pk>/', views.cours_delete, name='supprimer_cours'),
]