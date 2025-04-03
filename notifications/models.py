import uuid
from django.contrib.auth import get_user_model
from django.db import models

custom_user = get_user_model()

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(custom_user, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.recipient} at {self.sent_at}"
