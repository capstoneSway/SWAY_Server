from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings

class Lightning(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'inProgress', '모집 중'
        DONE = 'done', '마감'
        CANCELED = 'canceled', '취소'

    class Category(models.TextChoices):
        TOUR = 'tour', '여행'
        EATING = 'eating', '맛집'
        EXERCISE = 'exercise', '운동'
        ELSE = 'else', '기타'

    # host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_meetups')
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hosted_meetups')
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    current_participant = models.IntegerField(default=0)
    max_participant = models.IntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.IN_PROGRESS)
    category = models.CharField(max_length=10, choices=Category.choices)
    background_pic = models.CharField(max_length=255, blank=True)
    like = models.IntegerField(default=0)

    def __str__(self):
        return self.title