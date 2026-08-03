from django.contrib.auth import get_user_model
from django.db import models


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('pending', 'В обработке'),
        ('published', 'Опубликовано'),
    )

    title = models.CharField(max_length=100)
    content = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)

    status = models.CharField(
        choices=STATUS_CHOICES,
        default=STATUS_CHOICES[0][0]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                               related_name='posts')
    cover = models.ImageField(upload_to='post_covers', blank=True, null=True)

    def __str__(self):
        return f'Post {self.title}'

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='blog_post_status_idx'),
            models.Index(fields=['title'], name='blog_post_title_idx'),
            models.Index(fields=['created_at'], name='blog_post_created_idx'),
            models.Index(fields=['updated_at'], name='blog_post_updated_idx'),
            models.Index(fields=['likes'], name='blog_post_likes_idx'),
            models.Index(fields=['views'], name='blog_post_views_idx'),
        ]
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',  # tag_set
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                               related_name='comments')

    def __str__(self):
        return f'Comment {self.content}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Tag(models.Model):
    name = models.CharField(max_length=100)
    posts = models.ManyToManyField('Post', related_name='tags')

    def __str__(self):
        return self.name
