from django.contrib import admin
from .models import ProjectProposal, Project, ProjectPlan, ProjectMembership

@admin.register(ProjectProposal)
class ProjectProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'submitted_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'submitted_by__username', 'field', 'department')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'field', 'department', 'academic_year', 'proposal')
    list_filter = ('academic_year', 'field', 'department')
    search_fields = ('name', 'field', 'department')
    readonly_fields = ('proposal',)  # Keep proposal read-only to prevent accidental changes

@admin.register(ProjectPlan)
class ProjectPlanAdmin(admin.ModelAdmin):
    list_display = ('project', 'duration')
    search_fields = ('project__name',)
    readonly_fields = ('project',)  # Prevent accidental reassignment of the project

@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role')
    list_filter = ('role',)
    search_fields = ('project__name', 'user__username')
    raw_id_fields = ('user',)  # Improves selection performance for large user databases
