from django.urls import path
from . import views

app_name = 'eleves'

urlpatterns = [
    # Authentication
    path('eleves/', views.eleves, name='eleves'),
    path('add_eleves', views.add_eleves, name='add_eleves'),
    path('modifier_eleves', views.modifier_eleves, name='modifier_eleves'),

]