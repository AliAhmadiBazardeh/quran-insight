from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser with username field"""

    def create_user(self, username, password=None, **extra_fields):
        """Create and return a regular user with username and password"""
        if not username:
            raise ValueError(_('The username must be set'))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom User model"""
    first_name = models.CharField(_('نام'), max_length=150)
    last_name = models.CharField(_('نام خانوادگی'), max_length=150)
    username = models.CharField(
        _('نام کاربری'),
        max_length=10,
        unique=True)

    # Additional custom fields
    date_of_birth = models.DateField(_('تاریخ تولد'), null=True, blank=True)
    phone_number = models.CharField(_('موبایل'), max_length=20, blank=True)
    bio = models.TextField(_('بیوگرافی'), max_length=500, blank=True)

    # Required fields for AbstractBaseUser
    is_staff = models.BooleanField(_('عضو تیم مدیریت'), default=False)
    is_active = models.BooleanField(_('فعال'), default=True)
    date_joined = models.DateTimeField(_('تاریخ ثبت کاربر'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']


    def save(self, *args, **kwargs):
        if not self.password:
            self.set_password('admin')
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return str(self.full_name)