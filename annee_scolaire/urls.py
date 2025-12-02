# annee_scolaire/urls.py
from django.urls import path
from . import views

app_name = 'annee_scolaire'

urlpatterns = [
    path('changer-annee/<int:annee_id>/', views.changer_annee_actuelle, name='changer_annee_actuelle'),
]