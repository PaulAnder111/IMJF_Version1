from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    # Classes
    path('classes/', views.classes, name='classes'),
    path('classes/ajouter/', views.ajouter_classes, name='ajouter_classes'),
    path('classes/modifier/<int:classe_id>/', views.modifier_classes, name='modifier_classes'),

]