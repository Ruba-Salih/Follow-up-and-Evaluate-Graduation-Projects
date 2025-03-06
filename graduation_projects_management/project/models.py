from django.db import models
from django.conf import settings
from users.models import Role
from django.utils import timezone

# Project Proposal model – used to submit proposals.
class ProjectProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    title = models.CharField(
        max_length=200, 
        help_text="Name of the proposed project"
    )
    team_member_count = models.IntegerField(
        help_text="Number of team members required"
    )
    field = models.CharField(
        max_length=200, 
        help_text="Field or area of the project"
    )
    department = models.CharField(
        max_length=200, 
        help_text="Department responsible for the project"
    )
    description = models.TextField(
        help_text="Description of the project"
    )
    additional_comment = models.TextField(
        blank=True, 
        null=True, 
        help_text="Any additional comments"
    )
    attached_file = models.FileField(
        upload_to='project_proposals/', 
        blank=True, 
        null=True, 
        help_text="Optional file attachment"
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_proposals',
        help_text="User who submitted this proposal"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the proposal"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Proposal: {self.title} (Status: {self.get_status_display()})"


# Project model – stores an accepted project.
class Project(models.Model):
    name = models.CharField(
        max_length=200, 
        help_text="Name of the project"
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        help_text="Project description"
    )
    academic_year = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        help_text="Academic year"
    )
    field = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Field or area of the project"
    )
    department = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Department responsible for the project"
    )
    # Link back to the proposal that generated this project
    proposal = models.OneToOneField(
        ProjectProposal,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='accepted_project',
        help_text="The proposal that generated this project (if applicable)"
    )
    
    def __str__(self):
        return self.name


# Project Plan model – filled out by the supervisor once the project is underway.
class ProjectPlan(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='plan'
    )
    outputs = models.TextField(
        blank=True, 
        null=True, 
        help_text="Expected outputs"
    )
    goals = models.TextField(
        blank=True, 
        null=True, 
        help_text="Project goals"
    )
    duration = models.IntegerField(
        blank=True, 
        null=True, 
        help_text="Project duration (in weeks or months)"
    )
    tasks = models.TextField(
        blank=True, 
        null=True, 
        help_text="Project tasks"
    )
    
    def __str__(self):
        return f"Plan for {self.project.name}"

class ProjectMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'project', 'role']  # Prevent duplicate role assignments

    def __str__(self):
        return f"{self.user.username} - {self.role.name} in {self.project.title}"
