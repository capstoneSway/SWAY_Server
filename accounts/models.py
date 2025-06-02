from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
import uuid
from django.db import transaction
from lightning.models import LightningParticipation, Lightning
from noti.models import Notification

# Create your models here.

# 커스텀 유저 설정
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        
        user = self.model(username=username, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if not extra_fields.get('social_id'):
            extra_fields['social_id'] = f"superuser_{uuid.uuid4()}"

        return self.create_user(username, password, **extra_fields)

class User(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, blank=True, null=True, unique=True)
    profile_image = models.URLField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    social_id = models.CharField(max_length=100, unique=True, default="")
    social_type = models.CharField(max_length=30, default="")
    nationality = models.CharField(max_length=50, blank=True, null=True)
    national_code = models.CharField(max_length=10, blank=True, null=True)

    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


    objects = UserManager()

    def __str__(self):
        return self.email
    
    def delete_user_and_participations(self):
        with transaction.atomic():
            # 탈퇴한 사용자가 참여한 모든 LightningParticipation 삭제
            participations = LightningParticipation.objects.filter(user=self)
            for participation in participations:
                lightning = participation.lightning
                # Lightning 모임의 현재 참가자 수를 감소시킴
                lightning.current_participant -= 1
                lightning.update_status()
                participation.delete()  # 참여 기록 삭제

            # 사용자가 생성한 번개 모임의 상태를 CANCELED로 변경
            hosted_lightnings = Lightning.objects.filter(host=self)
            for lightning in hosted_lightnings:
                lightning.status = Lightning.Status.CANCELED
                lightning.is_active = False
                lightning.save()

                # 기 참가자들에게 알림 보내기
                participants = lightning.participants.exclude(id=self.id)
                for participant in participants:
                    Notification.objects.create(
                        user=participant,
                        type='번개모임',
                        event=lightning,
                        message=f"[{lightning.title}] 번개가 취소되었어요.",
                    )
                    
            # 탈퇴 처리 후 사용자 삭제
            self.delete()
