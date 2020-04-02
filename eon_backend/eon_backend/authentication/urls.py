from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import Login

app_name = 'authentication'

urlpatterns = [
    path('login', Login.as_view())
]