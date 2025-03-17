from django.db import models
from django.conf import settings
from project.models import Project
from django.utils import timezone


# -----------------------------
# Meeting-Related Models
# -----------------------------
MEETING_STATUS_CHOICES = [
    ('scheduled', 'Scheduled'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

class Meeting(models.Model):
    """
    Represents an offline meeting. One user requests the meeting, and multiple
    participants (students or non-students) are invited. After the meeting,
    the supervisor can update the status, add recommendations, and associate files.
    """
    meeting_id = models.AutoField(primary_key=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_meetings',
        help_text="User who requested the meeting (can be a student or non-student)."
    )
    date_time = models.DateTimeField(
        default=timezone.now,  # Automatically set to current time if not provided
        help_text="Scheduled date and time for the meeting."
    )
    status = models.CharField(
        max_length=20,
        choices=MEETING_STATUS_CHOICES,
        default='scheduled',
        help_text="Current status of the meeting."
    )
    recommendation = models.TextField(
        blank=True,
        null=True,
        help_text="Recommendation or notes added by the supervisor after the meeting."
    )

    def __str__(self):
        return f"Meeting {self.meeting_id} - {self.status}"


class MeetingParticipant(models.Model):
    """
    Associates users (students or non-students) with a meeting.
    Each participant's record includes an attendance status.
    """
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
        related_name='meetings_participated'
    )
    attendance_status = models.CharField(
        max_length=10,
        choices=ATTENDANCE_CHOICES,
        default='pending',
        help_text="Attendance status for this participant."
    )

    def __str__(self):
        return f"{self.user.username} ({self.attendance_status}) in Meeting {self.meeting.meeting_id}"


class MeetingFile(models.Model):
    """
    Stores files exchanged during a meeting.
    """
    file_id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='files'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_meeting_files'
    )
    file = models.FileField(
        upload_to='meeting_files/',
        help_text="File exchanged during the meeting."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File {self.file_id} for Meeting {self.meeting.meeting_id}"


# -----------------------------
# Project-Related File Model
# -----------------------------
class ProjectFile(models.Model):
    """
    Stores files associated with a project that are not part of a meeting.
    This could include documents, reports, or other files sent between users.
    """
    file_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project,  # Reference Project directly since it's already imported
        on_delete=models.CASCADE,
        related_name='project_files'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_project_files'
    )
    file = models.FileField(
        upload_to='project_files/',
        help_text="File associated with the project."
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of the file."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File {self.file_id} for Project {self.project.name}"
