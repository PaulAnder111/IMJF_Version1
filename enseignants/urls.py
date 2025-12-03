from django.urls import path
from . import views

app_name = 'enseignants'

urlpatterns = [
    path('', views.enseignant_list, name='enseignants'),
    path('ajouter/', views.create_enseignant, name='ajouter_enseignant'),
    path('<int:pk>/', views.enseignant_detail, name='enseignant_detail'),
    path('<int:pk>/modifier_ensegnant/', views.enseignant_update, name='modifier_enseignant'),
    path('<int:pk>/enseignant_archives/', views.enseignant_archiver, name='enseignant_archives'),
    path('<int:pk>/restaurer/', views.enseignant_restaurer, name='enseignant_restaurer'),
    path('enseignant_archives/', views.enseignant_archives, name='enseignant_archives'),
    path('exporter/', views.exporter_enseignants, name='exporter_enseignants'),
]
