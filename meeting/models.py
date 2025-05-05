from django.db import models
from django.conf import settings
from django.utils import timezone
from project.models import Project


# --------------------------------------
# Teacher's Recurring Weekly Availability
# --------------------------------------
class AvailableTime(models.Model):
    DAYS_OF_WEEK = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='available_times'
    )
    day = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('user', 'day', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.user.username} - {self.get_day_display()} ({self.start_time} to {self.end_time})"


# --------------------------------------
# Meeting-related models
# --------------------------------------

MEETING_STATUS_CHOICES = [
    ('pending', 'Pending'),        # Requested by student
    ('accepted', 'Accepted'),      # Accepted by teacher
    ('declined', 'Declined'),      # Declined by teacher
    ('scheduled', 'Scheduled'),    # Officially scheduled
    ('completed', 'Completed'),    # Finished and reviewed
    ('cancelled', 'Cancelled'),    # Cancelled meeting
]


class Meeting(models.Model):
    meeting_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meetings_as_teacher'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_meetings',
        help_text="User who requested the meeting"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings',
        help_text="Linked project if applicable"
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=MEETING_STATUS_CHOICES,
        default='pending'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        help_text="Message or agenda for the meeting"
    )
    recommendation = models.TextField(
        blank=True,
        null=True,
        help_text="Post-meeting notes or recommendations"
    )
    meeting_report = models.TextField(
        blank=True,
        null=True,
        help_text="Filled by student after meeting is completed"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meeting {self.meeting_id} with {self.teacher} [{self.status}]"

    def add_participants(self):
        """
        Automatically adds all students from the linked project to the meeting as participants.
        Assumes project.student_memberships.all() gives access to student user objects.
        """
        if self.project:
            for membership in self.project.student_memberships.all():
                MeetingParticipant.objects.get_or_create(
                    meeting=self,
                    user=membership.student,  # Assuming student is a User instance
                    defaults={
                        'attendance_status': 'pending',
                        'has_accepted': False
                    }
                )


class MeetingParticipant(models.Model):
    ATTENDANCE_CHOICES = [
        ('pending', 'Pending'),
        ('attended', 'Attended'),
        ('absent', 'Absent'),
    ]

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meeting_participations'
    )
    attendance_status = models.CharField(
        max_length=10,
        choices=ATTENDANCE_CHOICES,
        default='pending'
    )
    has_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.attendance_status}"


class MeetingFile(models.Model):
    file_id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='files'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meeting_files_uploaded'
    )
    file = models.FileField(upload_to='meeting_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"File {self.file_id} for Meeting {self.meeting.meeting_id}"
