from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('utilisateurs/', include('utilisateurs.urls')),
    path('eleves/', include('eleves.urls')),
    path('cours/', include('cours.urls')),
    path('enseignants/', include('enseignants.urls')),
    path('classes/', include('classes.urls')),
    path('matieres/', include('matieres.urls')),
    path('evaluations/', include('evaluations.urls')),
    path('notes/', include('notes.urls')),
    path('presences/', include('presences.urls')),
    path('', RedirectView.as_view(url='/utilisateurs/login/')),
      # Redirection racine
]