from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Category, Title, Response

class CustomUserCreationForm(UserCreationForm):
    """カスタムユーザー作成フォーム"""
    claude_api_key = forms.CharField(required=False, widget=forms.PasswordInput)
    chatgpt_api_key = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('claude_api_key', 'chatgpt_api_key')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_claude_api_key(self.cleaned_data["claude_api_key"])
        user.set_chatgpt_api_key(self.cleaned_data["chatgpt_api_key"])
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """カスタム認証フォーム"""
    class Meta:
        model = CustomUser

class UserProfileForm(forms.ModelForm):
    """ユーザープロフィール編集フォーム"""
    claude_api_key = forms.CharField(required=False, widget=forms.PasswordInput)
    chatgpt_api_key = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'claude_api_key', 'chatgpt_api_key']

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

class TitleForm(forms.ModelForm):
    """タイトルフォーム"""
    class Meta:
        model = Title
        fields = ['category', 'name']

class ResponseForm(forms.ModelForm):
    """回答作成フォーム"""
    class Meta:
        model = Response
        fields = ['title', 'question']

class ResponseUpdateForm(forms.ModelForm):
    """回答更新フォーム"""
    class Meta:
        model = Response
        fields = ['title', 'question', 'claude_response', 'chatgpt_response', 'final_response']