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
            raise ValueError('The email must be set')
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
    role = models.CharField(max_length=15, default='user')

    def __str__(self):
        return self.role

    class Meta:
        managed = True
        db_table = "role"
        verbose_name = "role"
        verbose_name_plural = "roles"


class Status(ModelBase):
    status = models.CharField(max_length=30)

    def __str__(self):
        return self.status

    class Meta:
        managed = True
        db_table = "status"
        verbose_name = "Status"
        verbose_name_plural = "Statuses"


class UserDetails(ModelBase):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=250, null=True, blank=True)
    contact_number = models.CharField(max_length=10)
    organization = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, default=1)
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)
