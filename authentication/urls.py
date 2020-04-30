"""
In this file we added all the url reference
"""
from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import Login, Register, change_user_password, reset_password, send_forget_password_mail, verify_token

urlpatterns = [
    path('login', Login.as_view(), name='login'),
    path('registration', Register.as_view(), name='registration'),
    path('token-refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password', change_user_password, name='change-password'),
    path('reset-password', reset_password, name='reset-password'),
    path('generate-code', send_forget_password_mail, name='send_verification_code'),
    path('verify-token', verify_token, name='verify_token')
]
