from django.db import models
from django.conf import settings
from django.utils import timezone
from project.models import Project

# Abstract base model with common report fields.
class BaseReport(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="%(class)s_reports",  # Dynamically set unique related names
        help_text="The project this report is for"
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_team_reports",
        help_text="Team members working on the project included in this report"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_created_reports",
        help_text="Supervisor who created this report"
    )
    report_date = models.DateField(default=timezone.now, help_text="Date of the report")
    progress = models.TextField(blank=True, null=True, help_text="Summary of overall progress")
    work_done = models.TextField(blank=True, null=True, help_text="Work completed during this period")
    work_remaining = models.TextField(blank=True, null=True, help_text="Work pending for the next period")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        member_names = ", ".join([member.username for member in self.team_members.all()])
        return f"Report for {self.project.name} for team members: {member_names} on {self.report_date}"

# Weekly or biweekly report model.
class WeeklyReport(BaseReport):
    challenges = models.TextField(blank=True, null=True, help_text="Challenges faced during the week")
    goals_next_period = models.TextField(blank=True, null=True, help_text="Goals for the next week/bi-week")

    class Meta:
        verbose_name = "Weekly Report"
        verbose_name_plural = "Weekly Reports"

# Monthly report model.
class MonthlyReport(BaseReport):
    overall_progress = models.TextField(blank=True, null=True, help_text="Overall monthly progress summary")
    month_plan = models.TextField(blank=True, null=True, help_text="The plan for the next month")

    class Meta:
        verbose_name = "Monthly Report"
        verbose_name_plural = "Monthly Reports"
