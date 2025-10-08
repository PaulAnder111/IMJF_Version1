from django.urls import path
from . import views

app_name = 'enseignants'

urlpatterns = [
    path('', views.enseignants, name='enseignants'),
]