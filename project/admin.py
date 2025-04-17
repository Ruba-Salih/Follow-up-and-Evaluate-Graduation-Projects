from django.contrib import admin
from .models import (
    ProjectProposal,
    Project,
    ProjectPlan,
    ProjectMembership,
    StudentProjectMembership,
    AnnualGrade,
    FeedbackExchange,
)

@admin.register(ProjectProposal)
class ProjectProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'submitted_by', 'teacher_status', 'coordinator_status', 'created_at', 'updated_at')
    list_filter = ('teacher_status', 'coordinator_status', 'department')
    search_fields = ('title', 'description', 'submitted_by__username')
    ordering = ('-created_at',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'supervisor', 'coordinator', 'academic_year', 'field')
    list_filter = ('academic_year', 'field', 'department')
    search_fields = ('name', 'supervisor__username', 'coordinator__username', 'field')
    ordering = ('name',)


@admin.register(ProjectPlan)
class ProjectPlanAdmin(admin.ModelAdmin):
    list_display = ('project', 'duration')
    list_filter = ('duration',)
    search_fields = ('project__name',)


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'group_id')
    list_filter = ('project', 'role')
    search_fields = ('user__username', 'project__name', 'role__name')


@admin.register(StudentProjectMembership)
class StudentProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('student', 'project', 'group_id')
    list_filter = ('project',)
    search_fields = ('student__username', 'project__name')


@admin.register(AnnualGrade)
class AnnualGradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'supervisor', 'project', 'grade', 'created_at')
    list_filter = ('project', 'supervisor')
    search_fields = ('student__username', 'project__name', 'supervisor__username')


@admin.register(FeedbackExchange)
class FeedbackExchangeAdmin(admin.ModelAdmin):
    list_display = ('project', 'sender', 'receiver', 'created_at')
    list_filter = ('project', 'created_at')
    search_fields = ('project__name', 'sender__username', 'receiver__username')
    ordering = ('-created_at',)
