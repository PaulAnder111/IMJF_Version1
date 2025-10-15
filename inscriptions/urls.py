from . import views
from django.urls import path

app_name = 'inscriptions'

urlpatterns = [
    path('inscription_list/', views.inscription, name='inscription_list'),  
    path('create_inscription/', views.create_inscription, name='create_inscription'),
    path('updates_inscriptions/', views.updates_inscriptions, name='updates_inscriptions'),
    path('delete_inscription/', views.delete_inscription, name='delete_inscription'),
   ]