from django.contrib import admin

from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    search_fields = ('question', 'answer')
    ordering = ('-created_at',)
