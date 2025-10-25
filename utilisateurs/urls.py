
from django.urls import path
from . import views

app_name = 'utilisateurs'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('base/', views.base, name='base'),
     path('change-photo/', views.change_photo, name='change_photo'),
    path('change-password/', views.change_password, name='change_password'),

    
    # Dashboards
    path('dash_admin/', views.dashboard, name='dash_admin'),
    
    # User management (admin only)
    path('create_user/', views.create_user, name='create_user'),
    path('<int:user_id>/update_user/', views.update_user, name='update_user'),
    path('list_users/', views.list_users, name='list_users'),
    path('users/<int:user_id>/', views.view_user, name='afficher'),
     path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
]