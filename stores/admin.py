from django.contrib import admin

from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_hours', 'closed_days', 'phone', 'address', 'open_status')
    search_fields = ('name', 'address', 'phone')
    list_filter = ('closed_days',)

    @admin.display(description='営業状態')
    def open_status(self, obj):
        return '営業中' if obj.is_open_now() else '営業時間外'
