from django.urls import path
from . import views

app_name = 'cours'

urlpatterns = [
    # Cours
    path('cours/', views.cours, name='cours'),
]