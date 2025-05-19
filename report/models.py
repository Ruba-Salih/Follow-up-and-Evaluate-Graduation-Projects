from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from project.models import Project


class ProjectReport(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="team_reports",
        verbose_name=_("Project")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Created By")
    )
    report_date = models.DateField(
        default=timezone.now,
        verbose_name=_("Report Date")
    )
    progress = models.TextField(_("Progress"), blank=True, null=True)
    work_done = models.TextField(_("Work Done"), blank=True, null=True)
    work_remaining = models.TextField(_("Work Remaining"), blank=True, null=True)
    challenges = models.TextField(_("Challenges"), blank=True, null=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return f"{_('Team Report')}: {self.project.name} {_('on')} {self.report_date}"


class TeamMemberStatus(models.Model):
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
    ]

    report = models.ForeignKey(
        ProjectReport,
        on_delete=models.CASCADE,
        related_name='member_statuses',
        verbose_name=_("Report")
    )
    student = models.ForeignKey(
        'users.Student',
        on_delete=models.CASCADE,
        verbose_name=_("Student")
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    notes = models.TextField(_("Notes"), blank=True, null=True)

    class Meta:
        unique_together = ['report', 'student']
        verbose_name = _("Team Member Status")
        verbose_name_plural = _("Team Member Statuses")

    def __str__(self):
        return f"{self.student.username} - {self.status} {_('in report')} {self.report.id}"

# Monthly report model.
'''class MonthlyReport(BaseReport):
    overall_progress = models.TextField(blank=True, null=True, help_text="Overall monthly progress summary")
    month_plan = models.TextField(blank=True, null=True, help_text="The plan for the next month")

    class Meta:
        verbose_name = "Monthly Report"
        verbose_name_plural = "Monthly Reports"
'''