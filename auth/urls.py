from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.get_user_profile, name='get_user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('verify-email-update/', views.verify_email_update, name='verify_email_update'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('verify-token/', views.verify_token, name='verify_token'),
    path('refresh-token/', views.refresh_token, name='refresh_token'),
]