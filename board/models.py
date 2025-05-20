from django.db import models
from django.conf import settings

# Create your models here.
class Board(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    image = models.ImageField(upload_to='board_images/', null=True, blank=True)  # ← 추가

    def __str__(self):
        return self.title

class Comment(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    board = models.ForeignKey(Board, null=False, blank=False, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('self', related_name='reply', on_delete=models.SET_NULL, null=True, blank=True)
    parent_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='child_comments')
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
    
class BoardLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'board')


class CommentLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'comment')


class BoardScrap(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='scraps')

    class Meta:
        unique_together = ('user', 'board')


class Report(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    board = models.ForeignKey(Board, null=True, blank=True, on_delete=models.CASCADE, related_name='reports')
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE, related_name='reports')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('reporter', 'board'), ('reporter', 'comment')]

    def __str__(self):
        if self.board:
            return f"{self.reporter} reported Board #{self.board.id}"
        elif self.comment:
            return f"{self.reporter} reported Comment #{self.comment.id}"
