from django.contrib import admin
from .models import Announcement, AnnouncementFile

class AnnouncementFileInline(admin.TabularInline):
    model = AnnouncementFile
    extra = 1
    readonly_fields = ('uploaded_at',)
    # Optionally, you can add `uploaded_by` if you want to display/edit it in admin

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'deadline', 'is_active', 'get_audience_description')
    list_filter = ('is_active', 'created_at', 'deadline')
    search_fields = ('title', 'message')
    filter_horizontal = ('target_departments',)
    ordering = ('-created_at',)
    inlines = [AnnouncementFileInline]

    def get_audience_description(self, obj):
        return obj.get_audience_description()
    get_audience_description.short_description = "Audience"

@admin.register(AnnouncementFile)
class AnnouncementFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'announcement', 'uploaded_at', 'uploaded_by')
    list_filter = ('uploaded_at',)
    search_fields = ('file',)
    readonly_fields = ('uploaded_at',)
