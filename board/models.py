from django.db import models
from accounts.models import User

# Create your models here.
class Board(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    image = models.ImageField(upload_to='board_images/', null=True, blank=True)  # ← 추가

    def __str__(self):
        return self.title

class Comment(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    board = models.ForeignKey(Board, null=False, blank=False, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    parent_id = models.ForeignKey('self', related_name='reply', on_delete=models.SET_NULL, null=True, blank=True)
    parent_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='child_comments')
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
    
class BoardLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'board')


class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'comment')


class BoardScrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='scraps')

    class Meta:
        unique_together = ('user', 'board')