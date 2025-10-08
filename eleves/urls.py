from django.urls import path
from . import views

app_name = 'eleves'

urlpatterns = [
    # Authentication
    path('eleves/', views.eleves, name='eleves'),

]