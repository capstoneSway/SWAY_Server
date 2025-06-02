from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

def get_default_end_time():
    return timezone.now() + timedelta(days=1)

class Tag(models.TextChoices):
    HOSTED = 'hosted', '생성한 채팅방'
    PARTICIPATED = 'participated', '참가한 채팅방'
    IRRELEVANT = 'irrelevant', '관련 없음'

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
    is_active = models.BooleanField(default=True, null=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    meeting_date = models.DateTimeField(blank=False, null=False, default=timezone.now)
    end_time = models.DateTimeField(default=get_default_end_time)
    current_participant = models.IntegerField(default=0)
    max_participant = models.IntegerField(default=5, validators=[MinValueValidator(2), MaxValueValidator(6)])
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.IN_PROGRESS)
    category = models.CharField(max_length=10, choices=Category.choices, default=Category.TRAVEL)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.ALL)
    background_pic = models.CharField(max_length=255, blank=True)
    like = models.IntegerField(default=0)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through='LightningParticipation', related_name='joined_lightnings')

    def __str__(self):
        return self.title
    
    def update_status(self):
        if self.current_participant >= self.max_participant:
            self.status = self.Status.DONE
        else:
            self.status = self.Status.IN_PROGRESS
        self.save()

class LightningParticipation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lightning = models.ForeignKey('Lightning', on_delete=models.CASCADE)
    relation_tag = models.CharField(max_length=20, choices=Tag.choices, default=Tag.IRRELEVANT)