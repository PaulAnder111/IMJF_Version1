from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    # Classes
    path('', views.classe_list, name='classe_list'),
    path('ajouter_classes/', views.classe_create, name='ajouter_classes'),
    path('modifier_classes/<int:pk>/', views.classe_update, name='modifier_classes'),
    path('supprimer/<int:pk>/', views.classe_delete, name='classe_confirm_delete'),
]