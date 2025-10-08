from . import views
from django.urls import path

app_name = 'presences'

urlpatterns = [
    path('presences/', views.presence_list, name='presence_list'),
    # Ajoutez d'autres chemins URL pour les présences si nécessaire
]
