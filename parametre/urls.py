from django.urls import path
from . import views

app_name = 'parametre'

urlpatterns = [
    path('historique/', views.historique_list, name='historique'),
    path('historique/export_csv/', views.export_csv, name='export_csv'),

]
