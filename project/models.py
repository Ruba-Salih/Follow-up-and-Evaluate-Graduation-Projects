from django.db import models
from django.conf import settings
from users.models import Role
from university.models import Department

class ProjectProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    team_member_count = models.IntegerField()
    field = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    additional_comment = models.TextField(blank=True, null=True)
    attached_file = models.FileField(upload_to='project_proposals/', blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_proposals')
    proposed_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_proposals')
    team_members = models.ManyToManyField('users.Student', blank=True, related_name='team_proposals')
    teacher_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    coordinator_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    team_member_count = models.IntegerField(null=True)
    field = models.CharField(max_length=200, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    proposal = models.OneToOneField(ProjectProposal, on_delete=models.SET_NULL, blank=True, null=True, related_name='accepted_project')
    supervisor = models.ForeignKey('users.Supervisor', on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    coordinator = models.ForeignKey('users.Coordinator', on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    
    def __str__(self):
        return self.name


# =============================
# Project Plan Model
# =============================
class ProjectPlan(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='plan')
    completion_status = models.IntegerField(blank=True, null=True)

class ProjectGoal(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='goals')
    goal = models.TextField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.goal} (Project: {self.project.name})"


class ProjectTask(models.Model):
    STATUS_CHOICES = [
        ('to do', 'To Do'),
        ('in progress', 'In Progress'),
        ('done', 'Done'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    goal = models.ForeignKey(ProjectGoal, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    name = models.CharField(max_length=255)
    outputs = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    remaining_tasks = models.TextField(blank=True)
    deliverable_text = models.TextField(blank=True, null=True)
    deliverable_file = models.FileField(upload_to='task_deliverables/', blank=True, null=True)
    deadline_days = models.PositiveIntegerField(blank=True, null=True)
    assign_to = models.ForeignKey('users.Student', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    task_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to do')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProjectLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='project_logs')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    log_type = models.CharField(max_length=100, blank=True, null=True)
    attachment = models.FileField(upload_to='log_attachments/', null=True, blank=True)


class ProjectMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    group_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ['user', 'project', 'role']


class StudentProjectMembership(models.Model):
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, null=True, blank=True, related_name='project_membership')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='student_memberships', null=True, blank=True)
    proposal = models.ForeignKey(ProjectProposal, on_delete=models.CASCADE, related_name='student_proposal_memberships', null=True, blank=True)
    group_id = models.CharField(max_length=50, blank=True, null=True)


class AnnualGrade(models.Model):
    supervisor = models.ForeignKey('users.Supervisor', on_delete=models.CASCADE, related_name="supervised_annual_grades")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_annual_grades")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="annual_grades")
    grade = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("supervisor", "student", "project")


class FeedbackExchange(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback_exchanges')
    proposal = models.ForeignKey(ProjectProposal, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback_exchanges')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_feedbacks')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback_received')
    feedback_text = models.TextField(blank=True, null=True)
    feedback_file = models.FileField(upload_to='feedback_files/', blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
