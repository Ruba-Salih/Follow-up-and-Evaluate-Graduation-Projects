from django.contrib import admin
from .models import (
    ProjectProposal,
    Project,
    ProjectPlan,
    ProjectGoal,
    ProjectTask,
    ProjectLog,
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
    list_display = ('project', 'completion_status')
    list_filter = ('completion_status',)
    search_fields = ('project__name',)


@admin.register(ProjectGoal)
class ProjectGoalAdmin(admin.ModelAdmin):
    list_display = ('goal', 'project', 'duration', 'created_at')
    list_filter = ('project',)
    search_fields = ('goal', 'project__name')
    ordering = ('-created_at',)


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'assign_to', 'remaining_tasks', 'task_status', 'deadline_days')
    list_filter = ('task_status', 'project', 'assign_to')
    search_fields = ('name', 'project__name', 'assign_to__username')


@admin.register(ProjectLog)
class ProjectLogAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'log_type', 'timestamp')
    list_filter = ('log_type', 'timestamp', 'project')
    search_fields = ('message', 'project__name', 'user__username')


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'group_id')
    list_filter = ('project', 'role')
    search_fields = ('user__username', 'project__name', 'role__name')


@admin.register(StudentProjectMembership)
class StudentProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('student', 'project', 'group_id')
    list_filter = ('project', 'proposal')
    search_fields = ('student__username', 'project__name')


@admin.register(AnnualGrade)
class AnnualGradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'supervisor', 'project', 'grade', 'created_at')
    list_filter = ('project', 'supervisor')
    search_fields = ('student__username', 'project__name', 'supervisor__username')


@admin.register(FeedbackExchange)
class FeedbackExchangeAdmin(admin.ModelAdmin):
    list_display = ('project', 'sender', 'receiver', 'created_at')
    list_filter = ('project', 'task', 'created_at')
    search_fields = ('project__name', 'sender__username', 'receiver__username')
    ordering = ('-created_at',)
