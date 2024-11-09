# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Category, Title, Response
import re

class CustomUserCreationForm(UserCreationForm):
    """カスタムユーザー作成フォーム"""
    username = forms.CharField(
        label='ユーザー名',
        max_length=150,
        help_text='※半角英数字、@/./+/-/_ のみ使用できます。',
        error_messages={
            'required': 'ユーザー名は必須です。',
            'max_length': 'ユーザー名は150文字以下で入力してください。',
        }
    )
    email = forms.EmailField(
        label='メールアドレス',
        required=True,
        error_messages={
            'required': 'メールアドレスは必須です。',
            'invalid': '有効なメールアドレスを入力してください。',
        }
    )
    password1 = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput,
        error_messages={
            'required': 'パスワードは必須です。',
        }
    )
    password2 = forms.CharField(
        label='パスワード（確認）',
        widget=forms.PasswordInput,
        error_messages={
            'required': 'パスワード（確認）は必須です。',
        }
    )
    claude_api_key = forms.CharField(
        label='Claude APIキー',
        required=False,
        widget=forms.PasswordInput
    )
    chatgpt_api_key = forms.CharField(
        label='ChatGPT APIキー',
        required=False,
        widget=forms.PasswordInput
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'claude_api_key', 'chatgpt_api_key')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError('ユーザー名には半角英数字、@/./+/-/_ のみ使用できます。')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('このユーザー名は既に使用されています。')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('このメールアドレスは既に登録されています。')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('パスワードが一致しません。')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if self.cleaned_data["claude_api_key"]:
            user.set_claude_api_key(self.cleaned_data["claude_api_key"])
        if self.cleaned_data["chatgpt_api_key"]:
            user.set_chatgpt_api_key(self.cleaned_data["chatgpt_api_key"])
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """カスタム認証フォーム"""
    username = forms.CharField(
        label='ユーザー名',
        error_messages={
            'required': 'ユーザー名を入力してください。',
        },
        widget=forms.TextInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        })
    )
    password = forms.CharField(
        label='パスワード',
        error_messages={
            'required': 'パスワードを入力してください。',
        },
        widget=forms.PasswordInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        })
    )

    error_messages = {
        'invalid_login': 'ユーザー名またはパスワードが正しくありません。',
        'inactive': 'このアカウントは現在無効になっています。',
    }

class UserProfileForm(forms.ModelForm):
    """ユーザープロフィール編集フォーム"""
    claude_api_key = forms.CharField(required=False, widget=forms.PasswordInput)
    chatgpt_api_key = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'claude_api_key', 'chatgpt_api_key']
        error_messages = {
            'username': {
                'unique': 'このユーザー名は既に使用されています。',
            },
            'email': {
                'unique': 'このメールアドレスは既に登録されています。',
            }
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError('ユーザー名には半角英数字、@/./+/-/_ のみ使用できます。')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError('このメールアドレスは既に登録されています。')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["claude_api_key"]:
            user.set_claude_api_key(self.cleaned_data["claude_api_key"])
        if self.cleaned_data["chatgpt_api_key"]:
            user.set_chatgpt_api_key(self.cleaned_data["chatgpt_api_key"])
        if commit:
            user.save()
        return user

class CategoryForm(forms.ModelForm):
    """カテゴリフォーム"""
    class Meta:
        model = Category
        fields = ['name']
        error_messages = {
            'name': {
                'required': 'カテゴリ名を入力してください。',
                'max_length': 'カテゴリ名は100文字以下で入力してください。',
            }
        }

class TitleForm(forms.ModelForm):
    """タイトルフォーム"""
    class Meta:
        model = Title
        fields = ['category', 'name']
        error_messages = {
            'category': {
                'required': 'カテゴリを選択してください。',
            },
            'name': {
                'required': 'タイトル名を入力してください。',
                'max_length': 'タイトル名は200文字以下で入力してください。',
            }
        }

class ResponseForm(forms.ModelForm):
    """回答作成フォーム"""
    class Meta:
        model = Response
        fields = ['title', 'question']
        error_messages = {
            'title': {
                'required': 'タイトルを選択してください。',
            },
            'question': {
                'required': '質問を入力してください。',
            }
        }

class ResponseUpdateForm(forms.ModelForm):
    """回答更新フォーム"""
    class Meta:
        model = Response
        fields = ['title', 'question', 'claude_response', 'chatgpt_response', 'final_response']
        error_messages = {
            'title': {
                'required': 'タイトルを選択してください。',
            },
            'question': {
                'required': '質問を入力してください。',
            }
        }