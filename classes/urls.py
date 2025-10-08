from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    # Classes
    path('classes/', views.classes, name='classes'),
]