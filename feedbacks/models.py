from django.db import models
from django.conf import settings
from project.models import Project  # Adjust if your project model is elsewhere


class ProjectFeedback(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='feedbacks')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_project_feedbacks'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_project_feedbacks'
    )
    title = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title or 'Feedback'} from {self.sender}"


class FeedbackReply(models.Model):
    feedback = models.OneToOneField(ProjectFeedback, on_delete=models.CASCADE, related_name='reply')
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to Feedback {self.feedback.id}"


class FeedbackFile(models.Model):
    feedback = models.ForeignKey(ProjectFeedback, on_delete=models.CASCADE, related_name='files')
    reply = models.ForeignKey(FeedbackReply, null=True, blank=True, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='feedback_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.reply:
            return f"Reply file for Feedback {self.feedback.id}"
        return f"Student file for Feedback {self.feedback.id}"


""" 
class ProjectFeedback(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='feedbacks')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_project_feedbacks'  
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_project_feedbacks' 
    )
    message = models.TextField(blank=True, null=True)
    is_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.sender} to {self.receiver} ({'Reply' if self.is_reply else 'Initial'})"


class FeedbackFile(models.Model):
    feedback = models.ForeignKey(ProjectFeedback, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='feedback_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for Feedback {self.feedback.id}"
 """