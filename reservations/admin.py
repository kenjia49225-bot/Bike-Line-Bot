from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'kind', 'name', 'preferred_datetime', 'detail', 'phone', 'status', 'created_at')
    list_filter = ('kind', 'status')
    search_fields = ('user_id', 'name', 'preferred_datetime', 'detail', 'phone')
    list_editable = ('status',)
    ordering = ('-created_at',)
