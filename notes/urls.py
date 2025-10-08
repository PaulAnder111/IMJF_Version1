from . import views
from django.urls import path

app_name = 'notes'

urlpatterns = [
    path('notes/', views.note_list, name='notes_list'),
    # Ajoutez d'autres chemins URL pour les notes si nécessaire
]