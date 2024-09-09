from django.contrib import admin
from .models import UserAPIKeys, Category, Title, Response

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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    list_filter = ('user',)
    search_fields = ('name', 'user__username')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user" and not request.user.is_superuser:
            kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'user')
    list_filter = ('category', 'user')
    search_fields = ('name', 'category__name', 'user__username')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user" and not request.user.is_superuser:
            kwargs["queryset"] = User.objects.filter(id=request.user.id)
        elif db_field.name == "category" and not request.user.is_superuser:
            kwargs["queryset"] = Category.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('title', 'user')
    search_fields = ('content', 'title__name', 'user__username')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user" and not request.user.is_superuser:
            kwargs["queryset"] = User.objects.filter(id=request.user.id)
        elif db_field.name == "title" and not request.user.is_superuser:
            kwargs["queryset"] = Title.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)