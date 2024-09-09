from django.db import models
from django.contrib.auth.models import User

class UserAPIKeys(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    claude_api_key = models.CharField(max_length=255, blank=True, null=True)
    chatgpt_api_key = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s API Keys"

    class Meta:
        verbose_name = "User API Keys"
        verbose_name_plural = "User API Keys"