import uuid
from django.db import models
from django.conf import settings

class Meeting(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
    ]
    
    # The user (student or supervisor) who requested the meeting.
    initiator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='meetings_initiated',
        help_text="User who requested the meeting"
    )
    
    scheduled_datetime = models.DateTimeField(
        help_text="Date and time when the meeting is scheduled"
    )
    notification_message = models.TextField(
        blank=True, 
        null=True, 
        help_text="Message included with the meeting invitation"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text="Current status of the meeting request"
    )
    recommendation = models.TextField(
        blank=True, 
        null=True, 
        help_text="Recommendations or notes added after the meeting"
    )
    # Users who participated or are intended to participate.
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='meetings_participated',
        blank=True,
        help_text="Users invited to or attending this meeting"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meeting {self.pk} on {self.scheduled_datetime} (Status: {self.status})"


class MeetingFile(models.Model):
    # Unique identifier for each file using a UUID.
    file_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    meeting = models.ForeignKey(
        Meeting, 
        on_delete=models.CASCADE, 
        related_name='files'
    )
    file = models.FileField(
        upload_to='meeting_files/', 
        help_text="File related to the meeting"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File {self.file_id} for Meeting {self.meeting.pk}"
