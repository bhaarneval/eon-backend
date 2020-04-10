from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class ModelBase(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True, verbose_name="Date Range Filter")

    class Meta:
        abstract = True


class ActiveModel(ModelBase):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        extra_fields.setdefault('is_active', True)
        if not email:
            raise ValueError('The email must be set')
        if 'username' in extra_fields:
            extra_fields.pop('username')
        user = self.model(username=email, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, ModelBase):
    email = models.EmailField(unique=True)

    objects = UserManager()

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"


class Role(ModelBase):
    role = models.CharField(max_length=15)

    def __str__(self):
        return self.role

    class Meta:
        managed = True
        db_table = "role"
        verbose_name = "role"
        verbose_name_plural = "roles"


class VerificationCode(ActiveModel):
    email = models.EmailField()
    code = models.CharField(max_length=4)

    def __str__(self):
        return self.email

    class Meta:
        managed = True
        db_table = "verification_code"
        verbose_name = "verification_code"
        verbose_name_plural = "verification_codes"
