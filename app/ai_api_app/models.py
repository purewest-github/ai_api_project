# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    """カスタムユーザーモデル"""
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='ユーザー名には半角英数字、@/./+/-/_ のみ使用できます。',
            ),
        ],
        error_messages={
            'unique': "このユーザー名は既に使用されています。",
        }
    )
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': "このメールアドレスは既に登録されています。",
        }
    )
    claude_api_key = models.CharField(max_length=255, blank=True, null=True)
    chatgpt_api_key = models.CharField(max_length=255, blank=True, null=True)

    def set_claude_api_key(self, raw_key):
        """Claude APIキーを暗号化して保存"""
        if raw_key:
            self.claude_api_key = make_password(raw_key)

    def set_chatgpt_api_key(self, raw_key):
        """ChatGPT APIキーを暗号化して保存"""
        if raw_key:
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
    claude_response = models.TextField(blank=True)
    chatgpt_response = models.TextField(blank=True)
    final_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response for {self.title.name}"