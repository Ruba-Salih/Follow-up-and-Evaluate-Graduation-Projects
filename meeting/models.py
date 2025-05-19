from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from project.models import Project

# --------------------------------------
# Teacher's Recurring Weekly Availability
# --------------------------------------
class AvailableTime(models.Model):
    DAYS_OF_WEEK = [
        ('mon', _('Monday')),
        ('tue', _('Tuesday')),
        ('wed', _('Wednesday')),
        ('thu', _('Thursday')),
        ('fri', _('Friday')),
        ('sat', _('Saturday')),
        ('sun', _('Sunday')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='available_times',
        verbose_name=_("User")
    )
    day = models.CharField(_("Day of Week"), max_length=3, choices=DAYS_OF_WEEK)
    start_time = models.TimeField(_("Start Time"))
    end_time = models.TimeField(_("End Time"))

    class Meta:
        unique_together = ('user', 'day', 'start_time', 'end_time')
        verbose_name = _("Available Time")
        verbose_name_plural = _("Available Times")

    def __str__(self):
        return f"{self.user.username} - {self.get_day_display()} ({self.start_time} to {self.end_time})"


# --------------------------------------
# Meeting-related models
# --------------------------------------

MEETING_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('accepted', _('Accepted')),
    ('declined', _('Declined')),
    ('scheduled', _('Scheduled')),
    ('completed', _('Completed')),
    ('cancelled', _('Cancelled')),
]


class Meeting(models.Model):
    meeting_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meetings_as_teacher',
        verbose_name=_("Teacher")
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_meetings',
        help_text=_("User who requested the meeting"),
        verbose_name=_("Requested By")
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings',
        help_text=_("Linked project if applicable"),
        verbose_name=_("Project")
    )
    start_datetime = models.DateTimeField(_("Start Time"))
    end_datetime = models.DateTimeField(_("End Time"))
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=MEETING_STATUS_CHOICES,
        default='pending'
    )
    comment = models.TextField(
        _("Comment"),
        blank=True,
        null=True,
        help_text=_("Message or agenda for the meeting")
    )
    recommendation = models.TextField(
        _("Recommendation"),
        blank=True,
        null=True,
        help_text=_("Post-meeting notes or recommendations")
    )
    meeting_report = models.TextField(
        _("Meeting Report"),
        blank=True,
        null=True,
        help_text=_("Filled by student after meeting is completed")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{_('Meeting')} {self.meeting_id} {_('with')} {self.teacher} [{self.status}]"

    def add_participants(self):
        """
        Automatically adds all students from the linked project to the meeting as participants.
        Assumes project.student_memberships.all() gives access to student user objects.
        """
        if self.project:
            for membership in self.project.student_memberships.all():
                MeetingParticipant.objects.get_or_create(
                    meeting=self,
                    user=membership.student,
                    defaults={
                        'attendance_status': 'pending',
                        'has_accepted': False
                    }
                )


class MeetingParticipant(models.Model):
    ATTENDANCE_CHOICES = [
        ('pending', _('Pending')),
        ('attended', _('Attended')),
        ('absent', _('Absent')),
    ]

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name=_("Meeting")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meeting_participations',
        verbose_name=_("Participant")
    )
    attendance_status = models.CharField(
        _("Attendance Status"),
        max_length=10,
        choices=ATTENDANCE_CHOICES,
        default='pending'
    )
    has_accepted = models.BooleanField(_("Has Accepted"), default=False)

    def __str__(self):
        return f"{self.user.username} - {self.attendance_status}"


class MeetingFile(models.Model):
    file_id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_("Meeting")
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meeting_files_uploaded',
        verbose_name=_("Uploaded By")
    )
    file = models.FileField(_("File"), upload_to='meeting_files/')
    uploaded_at = models.DateTimeField(_("Uploaded At"), auto_now_add=True)
    description = models.TextField(_("Description"), blank=True, null=True)

    def __str__(self):
        return f"{_('File')} {self.file_id} {_('for Meeting')} {self.meeting.meeting_id}"
