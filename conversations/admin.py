from django.contrib import admin

from .models import Conversation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'role', 'content_short', 'needs_human', 'status', 'created_at')
    list_filter = ('role', 'needs_human', 'status', 'created_at')
    search_fields = ('user_id', 'content')
    ordering = ('-created_at',)
    list_editable = ('needs_human', 'status')
    date_hierarchy = 'created_at'
    actions = ('mark_as_resolved',)

    @admin.display(description='メッセージ内容')
    def content_short(self, obj):
        return obj.content[:50]

    @admin.action(description='選択した項目を解決済みにする')
    def mark_as_resolved(self, request, queryset):
        queryset.update(status=Conversation.Status.RESOLVED, needs_human=False)
        self.message_user(request, '選択した項目を解決済みにしました。')
