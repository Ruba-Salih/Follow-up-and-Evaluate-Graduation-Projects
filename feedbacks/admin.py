from django.contrib import admin
from .models import ProjectFeedback, FeedbackReply, FeedbackFile

@admin.register(ProjectFeedback)
class ProjectFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'sender', 'teacher', 'title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sender__username', 'teacher__username', 'title', 'message')


@admin.register(FeedbackReply)
class FeedbackReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'feedback', 'created_at')
    search_fields = ('feedback__id', 'message')


@admin.register(FeedbackFile)
class FeedbackFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'feedback', 'reply', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('feedback__id',)
