from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images/', default='profile_images/blank-profile-picture.png')
    location = models.CharField(max_length=100, blank=True)
    notification_preference = models.CharField(
        max_length=10,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('in_app', 'In-App Notification')
        ],
        default='in_app'
    )

    def __str__(self):
        return f"Profile of {self.user.username}"

class Category1(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        unique_slug = self.slug
        num = 1
        while Category1.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{self.slug}-{num}'
            num += 1
        self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Category2(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        unique_slug = self.slug
        num = 1
        while Category2.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{this.slug}-{num}'
            num += 1
        self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, editable=False)
    body = models.TextField()
    image = models.ImageField(upload_to='blog-post-images/', blank=False, null=False ,default='images/default.png')
    video = models.FileField(upload_to='blog-post-videos/', blank=True, null=True)
    first_category = models.ForeignKey(Category1, on_delete=models.CASCADE, related_name='posts')
    second_category = models.ForeignKey(Category2, on_delete=models.CASCADE, related_name='posts')
    status = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    number_of_clicks = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        unique_slug = self.slug
        num = 1
        while Post.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{self.slug}-{num}'
            num += 1
        self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments') 
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}: {self.body[:20]}...'