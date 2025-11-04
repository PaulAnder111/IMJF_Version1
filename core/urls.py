# urls.py nan pwojè a (pa nan app la)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('utilisateurs.urls')),
]

# Handlers erè
handler400 = 'utilisateurs.views.bad_request'
handler403 = 'utilisateurs.views.permission_denied'
handler404 = 'utilisateurs.views.page_not_found'
handler500 = 'utilisateurs.views.server_error'
