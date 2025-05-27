from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

def get_default_end_time():
    return timezone.now() + timedelta(days=1)

class Lightning(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'inProgress', '모집 중'
        DONE = 'done', '마감'
        CANCELED = 'canceled', '취소'

    class Category(models.TextChoices):
        TRAVEL = 'travel', '여행'
        FOODIE = 'foodie', '맛집'
        WORKOUT = 'workout', '운동'
        OTHERS = 'others', '기타'

    class Gender(models.TextChoices):
        ALL = 'all', '모두'
        MALE = 'male', '남자만'
        FEMALE = 'female', '여자만'

    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hosted_meetups')
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(default=get_default_end_time)
    current_participant = models.IntegerField(default=0)
    max_participant = models.IntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.IN_PROGRESS)
    category = models.CharField(max_length=10, choices=Category.choices, default=Category.TRAVEL)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.ALL)
    background_pic = models.CharField(max_length=255, blank=True)
    like = models.IntegerField(default=0)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='joined_lightnings', blank=True)

    def __str__(self):
        return self.title