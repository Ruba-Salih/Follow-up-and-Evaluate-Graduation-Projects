from django.contrib import admin
from .models import (
    Meeting, 
    MeetingParticipant, 
    MeetingFile, 
    AvailableTime
)

# AvailableTime Admin
@admin.register(AvailableTime)
class AvailableTimeAdmin(admin.ModelAdmin):
    list_display = ('user', 'day', 'start_time', 'end_time')
    list_filter = ('day', 'user')
    search_fields = ('user__username', 'start_time', 'end_time')
    ordering = ('user', 'day', 'start_time')


# Meeting Admin
@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('meeting_id', 'requested_by', 'teacher', 'start_datetime', 'end_datetime', 'meeting_report', 'status')  # Use 'meeting_id' instead of 'meeting'
    list_filter = ('status', 'start_datetime')
    search_fields = ('requested_by__username', 'teacher__username', 'meeting_id')
    ordering = ('-start_datetime',)


# MeetingParticipant Admin
@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'user', 'attendance_status', 'has_accepted')
    list_filter = ('attendance_status', 'has_accepted')
    search_fields = ('meeting__meeting_id', 'user__username')
    ordering = ('meeting', 'user')

# MeetingFile Admin
@admin.register(MeetingFile)
class MeetingFileAdmin(admin.ModelAdmin):
    list_display = ('file_id', 'meeting', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('meeting__meeting_id', 'uploaded_by__username')
    ordering = ('-uploaded_at',)
