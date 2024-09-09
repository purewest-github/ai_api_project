from django import forms
from .models import UserAPIKeys

class UserAPIKeysForm(forms.ModelForm):
    class Meta:
        model = UserAPIKeys
        fields = ['claude_api_key', 'chatgpt_api_key']
        widgets = {
            'claude_api_key': forms.PasswordInput(render_value=True),
            'chatgpt_api_key': forms.PasswordInput(render_value=True),
        }