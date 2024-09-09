from django.contrib import admin
from .models import UserAPIKeys

@admin.register(UserAPIKeys)
class UserAPIKeysAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_claude_key', 'has_chatgpt_key')
    
    def has_claude_key(self, obj):
        return bool(obj.claude_api_key)
    has_claude_key.boolean = True
    has_claude_key.short_description = 'Has Claude API Key'

    def has_chatgpt_key(self, obj):
        return bool(obj.chatgpt_api_key)
    has_chatgpt_key.boolean = True
    has_chatgpt_key.short_description = 'Has ChatGPT API Key'