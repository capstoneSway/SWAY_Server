from django.db import models
from django.db import models
from django.conf import settings

# ENUM 타입 정의 (번개모임, 채팅, 게시판)
class NotificationType(models.TextChoices):
    LIGHTNING = '번개모임', '번개 모임'
    CHAT = '채팅', '채팅'
    COMMENTS = '댓글', '댓글'
    REPLIES = '대댓글', '대댓글'

class Notification(models.Model):
    # 알림을 받는 대상자 (유저)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    type = models.CharField(
        max_length=10,
        choices=NotificationType.choices
    )

    event = models.ForeignKey(
        'lightning.Lightning',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    # chat = models.ForeignKey(
    #     'chat.ChatRoom',
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name='notifications'
    # )

    board = models.ForeignKey(
        'board.Board',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_type_display()}] {self.message[:20]}"

    class Meta:
        ordering = ['-created_at']