# from django.urls import path
# from . import views


# urlpatterns = [
#     path('login/', views.login_view, name='login'),
#     path('logout/', views.logout_view, name='logout_view'),
#     path('base/', views.base, name='base'),
#     path('dash_admin/', views.dashboard, name='dash_admin'),
#     path('list_users/', views.list_users, name='list_users'),
#     path('create_user/', views.create_user, name='create_user'),
#     path('update_user/', views.update_user, name='update_user'),
# ]


from django.urls import path
from . import views

app_name = 'utilisateurs'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('base/', views.base, name='base'),
    
    # Dashboards
    path('dash_admin/', views.dashboard, name='dash_admin'),
    path('dash_secretaire/', views.secretaire_required, name='dash_secretaire'),
    # path('dash_directeur/', views.directeur_required, name='dash_directeur'),
    # path('dashboard/teacher/', views.dashboard_teacher, name='dashboard_teacher'),
    
    # User management (admin only)
    path('create_user/', views.create_user, name='create_user'),
    path('<int:user_id>/update_user/', views.update_user, name='update_user'),
    path('list_users/', views.list_users, name='list_users'),
     path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
]