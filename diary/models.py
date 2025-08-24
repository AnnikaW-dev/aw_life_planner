from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DiaryEntry(models.Model):
    MOOD_CHOICES = [
        ('happy', '😊 Happy'),
        ('sad', '😢 Sad'),
        ('neutral', '😐 Neutral'),
        ('excited', '🤩 Excited'),
        ('anxious', '😰 Anxious'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=200)
    content = models.CharField()
    mood = models.CharField(
        max_length=50, choices=MOOD_CHOICES, null=True, blank=True
        )
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            '-date',
            '-created_at',
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}"
