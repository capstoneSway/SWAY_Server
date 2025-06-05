from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class NotiSetting(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment_noti = models.BooleanField(default=True)
    reply_noti = models.BooleanField(default=True)
    meetup_noti = models.BooleanField(default=True)
    chat_noti = models.BooleanField(default=True)


class Restriction(models.Model):
    RESTRICTION_TYPE_CHOICES = [ #추후 추가 가능
    ('board_ban', 'Board Ban'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restrictions')
    reason = models.TextField()
    restriction_type = models.CharField(max_length=20, choices=RESTRICTION_TYPE_CHOICES)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    duration_days = models.PositiveIntegerField(null=True, blank=True, help_text="None: Permanently ban")
    release_at = models.DateTimeField(null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        # created_at이 아직 없을 경우 현재 시간 기준 계산
        base_time = timezone.now()
        if self.duration_days is not None:
            self.release_at = base_time + timedelta(days=self.duration_days)
        else:
            self.release_at = None
        super().save(*args, **kwargs)

    def is_active(self):
        if self.duration_days is None:
            return True
        return timezone.now() < self.release_at
    
    def __str__(self):
        duration_text = f"{self.duration_days} day(s)" if self.duration_days is not None else "Permanently"
        return f"{self.user.nickname} - {self.get_restriction_type_display()} ({duration_text})"

class Feedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('bug', 'Bug Report'),
        ('suggestion', 'Suggestion'),
        ('etc', 'Other'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    title = models.CharField(max_length=100)
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_feedback_type_display()}"
    
class BlockUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocker')  # 차단하는 유저
    blocked_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocked')  # 차단당한 유저
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blocked_user')  # 중복 차단 방지

    def __str__(self):
        return f"{self.user} blocked {self.blocked_user}"
