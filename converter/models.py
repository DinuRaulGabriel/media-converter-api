from django.db import models
from django.contrib.auth.models import User


class Download(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads')
    title = models.CharField(max_length=255)
    source_url = models.URLField()
    file_path = models.CharField(max_length=500)
    format = models.CharField(max_length=50, default="mp3")
    created_at = models.DateTimeField(auto_now_add=True)
    quality = models.CharField(max_length=10, default="medium")

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    download = models.ForeignKey(
        Download,
        on_delete=models.CASCADE,
        related_name="favorite_entries"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "download"],
                name="unique_user_favorite_download"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} <3 {self.download.title}"


class ConversionPreset(models.Model):
    FORMAT_CHOICES = [
        ("mp3", "mp3"),
        ("mp4", "mp4"),
    ]

    QUALITY_CHOICES = [
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversion_presets")
    name = models.CharField(max_length=100)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES, default="medium")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_preset_name_per_user"
            )
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.format}/{self.quality})"