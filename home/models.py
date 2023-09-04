from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# reverse hamun url ast


class Post(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')
    # related name bara in ek age bekhaymdakhele rabete baraks harekat konim b kar mire
    body = models.TextField()
    slug = models.SlugField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.user} * {self.slug}'

    def get_absolute_url(self):
        return reverse('home:post_detail', args=(self.id, self.slug))
    # dar index.html

    def likes_count(self):
        return self.pvotes.count()

    def user_can_like(self, user):
        user_like = user.uvotes.filter(post=self)
        # un likhayi k marbut b in post hasesh
        if user_like.exists():
            return True
            # age true biare yani karbar ino like karde
        return False


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='ucomments')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='pcomments')
    reply = models.ForeignKey(
        'Comment', models.CASCADE, related_name='rcomments', blank=True, null=True)
    is_reply = models.BooleanField(default=False)
    # esme model bayad dakhele '' bashe ya 'self' mizarim
    body = models.TextField(max_length=400)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.body[:30]}'


class Vote(models.Model):
    # vase like kardane posthas
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='uvotes')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='pvotes')

    def __str__(self):
        return f'{self.user} liked {self.post.slug}'
