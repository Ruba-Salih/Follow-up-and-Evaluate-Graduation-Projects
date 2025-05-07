from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'notification_type', 'sent_at', 'read')  # Display important fields
    list_filter = ('notification_type', 'read', 'sent_at')  # Filter by type, read status, and sent time
    search_fields = ('recipient__username', 'message')  # Search by recipient username and message content
    ordering = ('-sent_at',)  # Order by sent_at (most recent first)

    # Optionally add a custom method to display the 'read' status as a checkbox
    def read_display(self, obj):
        return "Yes" if obj.read else "No"
    read_display.short_description = "Read Status"  # Optional: Rename 'read' to 'Read Status' in the admin
