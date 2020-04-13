"""
From here our Application starts
url pattrern: /authentication/....
"""
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    initial url pattern : /authentication/...
    """
    name = 'authentication'
