from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin

# Create your models here.

# 커스텀 유저 설정
class UserManager(BaseUserManager):
  
    def create_user(self, email, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)        
        user = self.model(email=email, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

class User(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, blank=True)
    profile_image = models.URLField(blank=True, null=True)
    social_id = models.CharField(max_length=100, unique=True, default="")
    social_type = models.CharField(max_length=30, default="")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
