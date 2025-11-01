from django.urls import path
from . import views

app_name = 'inscriptions'

urlpatterns = [
    path('', views.inscription_list, name='inscription_list'),
    path('create_inscription/', views.inscription_create, name='create_inscription'),
    path('<int:pk>/updates_inscriptions/', views.inscription_update, name='updates_inscriptions'),
    path('<int:pk>/afficher_inscription/', views.inscription_detail, name='afficher_inscription'),
    path('<int:pk>/delete_inscription/', views.inscription_delete, name='delete_inscription'),
    path('<int:pk>/inscription_valider/', views.inscription_valider, name='inscription_valider'),  # ← Ajoute sa
]