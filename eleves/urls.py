from django.urls import path
from . import views

app_name = 'eleves'

urlpatterns = [
    path('eleve_list/', views.eleve_list, name='eleve_list'),  # liste actif
    path('<int:pk>/eleve_detail/', views.eleve_detail, name='eleve_detail'),
    path('<int:pk>/eleve_update/', views.eleve_update, name='eleve_update'),
    path('<int:pk>/eleve_delete/', views.eleve_delete, name='eleve_delete'),
    
    path('archives/', views.eleve_archives, name='eleve_archives'),  # liste archivés
    
    path('archive/<int:pk>/', views.eleve_archiver, name='eleve_archiver'),  # archive un élève
    path('restaurer/<int:pk>/', views.eleve_restaurer, name='eleve_restaurer'),  # restaurer un élève
]
