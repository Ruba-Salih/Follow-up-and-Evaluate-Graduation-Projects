from django.contrib import admin
from .models import (
    Meeting, 
    MeetingParticipant, 
    MeetingFile, 
    ProjectFile,
    AvailableTime  # Include AvailableTime model here
)

# Meeting Admin
@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('meeting_id', 'requested_by', 'teacher', 'date_time', 'status')  # Added 'teacher' for clarity
    list_filter = ('status', 'date_time')
    search_fields = ('requested_by__username', 'meeting_id', 'teacher__username')  # Search by teacher's username as well
    ordering = ('-date_time',)

# MeetingParticipant Admin
@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'user', 'attendance_status', 'has_accepted')  # Added 'has_accepted' for clarity
    list_filter = ('attendance_status', 'has_accepted')  # Filter by both attendance and acceptance status
    search_fields = ('meeting__meeting_id', 'user__username')

# MeetingFile Admin
@admin.register(MeetingFile)
class MeetingFileAdmin(admin.ModelAdmin):
    list_display = ('file_id', 'meeting', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('meeting__meeting_id', 'uploaded_by__username')

# ProjectFile Admin
@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('file_id', 'project', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('project__name', 'uploaded_by__username')

# AvailableTime Admin
@admin.register(AvailableTime)  # Add AvailableTime model to the admin
class AvailableTimeAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_day_display', 'start_time', 'end_time')  # Display user, day, and time slot
    list_filter = ('day', 'user')  # Filter by day and user
    search_fields = ('user__username', 'start_time', 'end_time')  # Search by username, start time, or end time
    ordering = ('user', 'day', 'start_time')  # Order by user, day, and start time

    # Optionally add a custom method to display the day name in the admin (if needed)
    def get_day_display(self, obj):
        return obj.get_day_display()
    get_day_display.short_description = 'Day'  # Optional: change the display name in the admin
