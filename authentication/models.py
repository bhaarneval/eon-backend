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
    email = models.EmailField(unique=True)

    objects = UserManager()

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"


class Role(ModelBase):
    role = models.CharField(max_length=15, default='user')

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "role"
        verbose_name = "role"
        verbose_name_plural = "roles"


class Status(ModelBase):
    status = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "status"
        verbose_name = "Status"
        verbose_name_plural = "Statuse"


class UserDetails(ModelBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, null=True, blank=True)
    contact_number = models.CharField(max_length=10)
    organization = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
