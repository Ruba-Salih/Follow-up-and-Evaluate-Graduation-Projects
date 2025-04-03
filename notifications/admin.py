from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'notification_type', 'sent_at')
    search_fields = ('recipient__username', 'message', 'notification_type')
    list_filter = ('notification_type', 'sent_at')
    ordering = ('-sent_at',)
