
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings 

User = get_user_model()

class Announcement(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('supervisor', 'Supervisor'),
        ('teacher', 'Teacher'),
        ('reader', 'Reader'),
        ('committee', 'Judgment Committee'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    target_roles = models.JSONField(
        help_text="List of roles (e.g., ['student', 'supervisor'])"
    )

    target_departments = models.ManyToManyField(
        'university.Department',
        blank=True,
        help_text="Leave empty to target all departments"
    )

    is_active = models.BooleanField(default=True)

    deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional deadline. After this time, the announcement won't be shown."
    )

    def __str__(self):
        return self.title

    def is_current(self):
        if not self.is_active:
            return False
        if self.deadline and self.deadline < timezone.now():
            return False
        return True

    def get_audience_description(self):
        role_list = ', '.join(self.target_roles)
        dept_list = ', '.join(d.name for d in self.target_departments.all())
        if self.target_departments.exists():
            return f"{role_list} in {dept_list}"
        return f"{role_list} in all departments"

class AnnouncementFile(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='announcement_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.file.name
