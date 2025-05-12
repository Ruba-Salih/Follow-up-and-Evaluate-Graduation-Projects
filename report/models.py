from django.db import models
from django.conf import settings
from django.utils import timezone
from project.models import Project

class ProjectReport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="team_reports")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_date = models.DateField(default=timezone.now)
    progress = models.TextField(blank=True, null=True)
    work_done = models.TextField(blank=True, null=True)
    work_remaining = models.TextField(blank=True, null=True)
    challenges = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Team Report: {self.project.name} on {self.report_date}"

class TeamMemberStatus(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    report = models.ForeignKey(ProjectReport, on_delete=models.CASCADE, related_name='member_statuses')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['report', 'student']

    def __str__(self):
        return f"{self.student.username} - {self.status} in report {self.report.id}"

# Monthly report model.
'''class MonthlyReport(BaseReport):
    overall_progress = models.TextField(blank=True, null=True, help_text="Overall monthly progress summary")
    month_plan = models.TextField(blank=True, null=True, help_text="The plan for the next month")

    class Meta:
        verbose_name = "Monthly Report"
        verbose_name_plural = "Monthly Reports"
'''