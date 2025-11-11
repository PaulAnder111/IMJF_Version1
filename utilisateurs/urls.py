# utilisateurs/urls.py
from django.urls import path
from . import views

app_name = 'utilisateurs'

urlpatterns = [
    # ------------------ Authentication ------------------
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ------------------ Dashboard ------------------
    path('dash_admin/', views.dashboard, name='dash_admin'),
    path('active-users/', views.active_users_list, name='active_users_list'),
    path('api/active-users/', views.get_active_users_json, name='get_active_users_json'),

    #------------------unauthorized------------------
    path('unauthorized/', views.unauthorized, name='unauthorized'),

    # path('db_error/',views.db_error,name='db_error'),

    # ------------------ Gestion Utilisateurs ------------------
    path('create_user/', views.create_user, name='create_user'),
    path('<int:user_id>/update_user/', views.update_user, name='update_user'),
    path('list_users/', views.list_users, name='list_users'),
    path('users/<int:user_id>/', views.a_view_user, name='afficher'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('change-photo/', views.change_photo, name='change_photo'),
    path('change-password/', views.update_password, name='change_password'),

    # ------------------ Password Reset Workflow ------------------
    path('password-reset/', views.request_reset_code, name='request_reset_code'),
    path('password-reset/verify-code/', views.verify_reset_code, name='verify_reset_code'),
    path('password-reset/new-password/', views.reset_password, name='reset_password'),
    path('get-notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
