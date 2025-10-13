from . import views
from django.urls import path

app_name = 'inscriptions'

urlpatterns = [
    path('', views.inscriptions, name='inscriptions'),  
]