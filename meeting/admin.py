from django.contrib import admin
from .models import (
    Meeting, 
    MeetingParticipant, 
    MeetingFile, 
    ProjectFile
)

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('meeting_id', 'requested_by', 'date_time', 'status')
    list_filter = ('status', 'date_time')
    search_fields = ('requested_by__username', 'meeting_id')
    ordering = ('-date_time',)


@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'user', 'attendance_status')
    list_filter = ('attendance_status',)
    search_fields = ('meeting__meeting_id', 'user__username')


@admin.register(MeetingFile)
class MeetingFileAdmin(admin.ModelAdmin):
    list_display = ('file_id', 'meeting', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('meeting__meeting_id', 'uploaded_by__username')


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('file_id', 'project', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('project__name', 'uploaded_by__username')
