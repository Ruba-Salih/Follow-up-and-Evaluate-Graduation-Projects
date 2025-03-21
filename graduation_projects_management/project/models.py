from django.db import models
from django.conf import settings
from django.utils import timezone
from users.models import Role  

# =============================
# Project Proposal Model
# =============================
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
    # For proposals from a student, this field should point to the teacher/coordinator to whom it is sent.
    proposed_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='received_proposals',
        help_text="If submitted by a student, specify the recipient (e.g. teacher/coordinator)"
    )
    # For student proposals: list the team members (their IDs and names) who will work on the project.
    team_members = models.ManyToManyField(
        'users.Student',
        blank=True,
        related_name='team_proposals',
        help_text="For student proposals: list the team members who will work on the project"
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


# =============================
# Project Model
# =============================
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
    # Link back to the proposal that generated this project (if applicable)
    proposal = models.OneToOneField(
        ProjectProposal,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='accepted_project',
        help_text="The proposal that generated this project (if applicable)"
    )
    # The teacher who accepts the proposal becomes the project's supervisor.
    supervisor = models.ForeignKey(
        'users.Supervisor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        help_text="Supervisor managing the project (teacher who accepted the proposal)"
    )
    # The coordinator responsible for this project.
    coordinator = models.ForeignKey(
        'users.Coordinator',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        help_text="Coordinator responsible for the project"
    )
    
    def __str__(self):
        return self.name


# =============================
# Project Plan Model
# =============================
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


# =============================
# Project Membership Model (for non-student roles)
# =============================
class ProjectMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    # Group identifier for members working in the same team on the project.
    group_id = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="Identifier for the group in the project"
    )

    class Meta:
        unique_together = ['user', 'project', 'role']

    def __str__(self):
        return f"{self.user.username} - {self.role.name} in {self.project.name}"


# =============================
# Student Project Membership Model (enforces one project per student)
# =============================
class StudentProjectMembership(models.Model):
    # A OneToOneField ensures that each student can only have one membership record.
    student = models.OneToOneField(
        'users.Student', 
        on_delete=models.CASCADE, 
        related_name='project_membership'
    )
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='student_memberships'
    )
    group_id = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="Identifier for the student's group in the project"
    )

    def __str__(self):
        return f"{self.student.username} in {self.project.name} (Group: {self.group_id})"


# =============================
# Annual Grade Model
# =============================
# Allows the supervisor to add an annual grade for each student in the project.
class AnnualGrade(models.Model):
    supervisor = models.ForeignKey(
        'users.Supervisor', 
        on_delete=models.CASCADE, 
        related_name="supervised_annual_grades"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="received_annual_grades"
    )
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name="annual_grades"
    )
    grade = models.FloatField(
        help_text="Annual grade given by the supervisor"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("supervisor", "student", "project")
         
    def __str__(self):
        return f"Annual Grade for {self.student.username} in {self.project.name} by {self.supervisor.username}"


# =============================
# Feedback Exchange Model
# =============================
# This model allows a user to send feedback related to a project.
# The sender selects a project and, optionally, a specific receiver.
# If no receiver is selected, the feedback will be sent to all students in the project.
# If a receiver is selected:
#   - If the receiver is a student, the feedback is intended for that student's group.
#   - If the receiver is not a student, the feedback is sent directly to that user.
class FeedbackExchange(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='feedback_exchanges',
        help_text="The project associated with this feedback."
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_feedbacks',
        help_text="User who sent the feedback."
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='feedback_received',
        help_text="The receiver of the feedback. If left blank, feedback is sent to all students in the project."
    )
    feedback_text = models.TextField(
        blank=True,
        null=True,
        help_text="Text of the feedback."
    )
    feedback_file = models.FileField(
        upload_to='feedback_files/',
        blank=True,
        null=True,
        help_text="Optional file attached with the feedback."
    )
    comment = models.TextField(
        blank=True,
        null=True,
        help_text="Optional comment."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.receiver:
            return f"Feedback from {self.sender.username} to {self.receiver.username} on {self.project.name}"
        else:
            return f"Feedback from {self.sender.username} to all students in {self.project.name}"
