from django.db import models
from django.conf import settings
from project.models import Project
from django.utils import timezone


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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='available_times')
    day = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('user', 'day', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.user.username} - {self.get_day_display()} ({self.start_time} to {self.end_time})"





# -----------------------------
# Meeting-Related Models
# -----------------------------
MEETING_STATUS_CHOICES = [
    ('pending', 'Pending'),        # Initially when requested by student
    ('accepted', 'Accepted'),      # Teacher accepts the request
    ('declined', 'Declined'),      # Teacher declines the request
    ('scheduled', 'Scheduled'),    # After teacher accepts, the meeting is scheduled
    ('completed', 'Completed'),    # After the meeting is done
    ('cancelled', 'Cancelled'),    # If the meeting is cancelled
]

class Meeting(models.Model):
    """
    Represents a meeting requested by a student or supervisor. Teacher can accept/decline the meeting request.
    """
    meeting_id = models.AutoField(primary_key=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='requested_meetings',
        help_text="User who requested the meeting (can be a student or non-student)."
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='meetings_as_teacher', 
        on_delete=models.CASCADE,
        help_text="Teacher the meeting is requested with."
    )
    project = models.ForeignKey(
        'project.Project', 
        related_name='meetings', 
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
        help_text="Project related to the meeting (if applicable)."
    )
    status = models.CharField(
        max_length=20,
        choices=MEETING_STATUS_CHOICES,
        default='pending',
        help_text="Current status of the meeting."
    )
    date_time = models.DateTimeField(
        default=timezone.now, 
        help_text="Scheduled date and time for the meeting."
    )
    recommendation = models.TextField(
        blank=True, 
        null=True, 
        help_text="Recommendation or notes added by the supervisor after the meeting."
    )
    comment = models.TextField(blank=True, null=True, help_text="Message added when scheduling the meeting.")

    def __str__(self):
        return f"Meeting {self.meeting_id} - {self.status}"

    def add_participants(self):
        """Add all students in the project to the meeting (if the meeting is project-related)."""
        if self.project:
            # Add all students from the project to the meeting
            for membership in self.project.student_memberships.all():
                MeetingParticipant.objects.create(
                    meeting=self,
                    user=membership.student,  # Assuming Student model has a user field
                    attendance_status='pending',  # Initially 'pending'
                    has_accepted=False,  # Initially no one has accepted the request
                )
        else:
            # If the meeting is not project-related, assume only the requesting student and teacher
            MeetingParticipant.objects.create(
                meeting=self,
                user=self.requested_by,  # The student requesting the meeting
                attendance_status='pending',
                has_accepted=False,
            )


class MeetingParticipant(models.Model):
    """
    Associates users (students or non-students) with a meeting.
    Each participant's record includes an attendance status and whether they've accepted the meeting.
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
    has_accepted = models.BooleanField(
        default=False,
        help_text="Whether the participant has accepted the meeting request."
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
