from django.urls import path
from . import views

app_name = 'enseignants'

urlpatterns = [
    path('liste/', views.enseignant_list, name='enseignants'),
    path('ajouter/', views.create_enseignant, name='ajouter_enseignant'),
    path('<int:pk>/', views.enseignant_detail, name='enseignant_detail'),
    path('<int:pk>/modifier/', views.enseignant_update, name='modifier_enseignant'),
    path('<int:pk>/archiver/', views.enseignant_archiver, name='enseignant_archiver'),
    path('<int:pk>/restaurer/', views.enseignant_restaurer, name='enseignant_restaurer'),
    path('archives/', views.enseignant_archives, name='enseignant_archives'),
]
