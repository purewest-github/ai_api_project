from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password

class CustomUser(AbstractUser):
    """カスタムユーザーモデル"""
    claude_api_key = models.CharField(max_length=255, blank=True, null=True)
    chatgpt_api_key = models.CharField(max_length=255, blank=True, null=True)

    def set_claude_api_key(self, raw_key):
        """Claude APIキーを暗号化して保存"""
        self.claude_api_key = make_password(raw_key)

    def set_chatgpt_api_key(self, raw_key):
        """ChatGPT APIキーを暗号化して保存"""
        self.chatgpt_api_key = make_password(raw_key)

class Category(models.Model):
    """カテゴリモデル"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ['user', 'name']

class Title(models.Model):
    """タイトルモデル"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['user', 'category', 'name']

class Response(models.Model):
    """回答モデル"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    question = models.TextField()
    claude_response = models.TextField()
    chatgpt_response = models.TextField()
    final_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response for {self.title.name}"