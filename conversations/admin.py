from django.contrib import admin

from .models import Conversation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'role', 'content', 'needs_human', 'status', 'created_at')
    list_filter = ('role', 'needs_human', 'status')
    search_fields = ('user_id', 'content')
    ordering = ('-created_at',)
    list_editable = ('needs_human', 'status')
