from django.urls import path
from .views import Login, Register

urlpatterns = [
    path('login', Login.as_view(), name='login'),
    path('registration', Register.as_view(), name='registeration'),
]
