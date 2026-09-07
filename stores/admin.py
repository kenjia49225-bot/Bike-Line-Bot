from django.contrib import admin

from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_hours', 'closed_days', 'phone', 'address')
    search_fields = ('name', 'address', 'phone')
