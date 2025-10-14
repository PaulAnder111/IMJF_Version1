from . import views
from django.urls import path

app_name = 'inscriptions'

urlpatterns = [
    path('inscription_list/', views.inscription, name='inscription_list'),  
    path('create_innscriptions/', views.create_inscrip,name='create_inscriptions.html'),
   ]