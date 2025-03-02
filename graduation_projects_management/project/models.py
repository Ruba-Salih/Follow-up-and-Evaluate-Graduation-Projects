from django.db import models
from django.conf import settings  # Reference to custom user model

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    academic_year = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class ProjectPlan(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='plan'
    )
    outputs = models.TextField(blank=True, null=True)
    goals = models.TextField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    tasks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Plan for {self.project.name}"


class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        (1, 'Reader'),
        (2, 'Committee Member'),
        (3, 'supervisor'),
    ]
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    role = models.IntegerField(choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('project', 'user', 'role')  # enforces one role per user per project

    def __str__(self):
        return f"{self.user.username} as {self.get_role_display()} in {self.project.name}"
