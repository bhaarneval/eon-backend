from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class ModelBase(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True, verbose_name="Date Range Filter")

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Phone Number must be set')
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser, ModelBase):
    email = models.EmailField(blank=True, null=True, unique=True)
    objects = UserManager()

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"

