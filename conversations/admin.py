from django.contrib import admin

from .models import Conversation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'role', 'content', 'created_at')
    list_filter = ('role',)
    search_fields = ('user_id', 'content')
    ordering = ('-created_at',)
