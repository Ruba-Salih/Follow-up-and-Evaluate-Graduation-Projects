from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from users.models import Role
from university.models import Department


class ProjectProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
    ]

    title = models.CharField(_("Title"), max_length=200)
    team_member_count = models.IntegerField(_("Team Member Count"))
    field = models.CharField(_("Field"), max_length=200)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Department"))
    description = models.TextField(_("Description"))
    additional_comment = models.TextField(_("Additional Comment"), blank=True, null=True)
    attached_file = models.FileField(_("Attached File"), upload_to='project_proposals/', blank=True, null=True)
    duration = models.IntegerField(_("Duration (Days)"), blank=True, null=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_proposals', verbose_name=_("Submitted By"))
    proposed_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_proposals', verbose_name=_("Proposed To"))
    team_members = models.ManyToManyField('users.Student', blank=True, related_name='team_proposals', verbose_name=_("Team Members"))
    teacher_status = models.CharField(_("Teacher Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    coordinator_status = models.CharField(_("Coordinator Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)


class Project(models.Model):
    name = models.CharField(_("Project Name"), max_length=200)
    description = models.TextField(_("Description"), blank=True, null=True)
    academic_year = models.CharField(_("Academic Year"), max_length=20, blank=True, null=True)
    team_member_count = models.IntegerField(_("Team Member Count"), null=True)
    field = models.CharField(_("Field"), max_length=200, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("Department"))
    duration = models.IntegerField(_("Duration (Days)"), blank=True, null=True)
    proposal = models.OneToOneField(ProjectProposal, on_delete=models.SET_NULL, blank=True, null=True, related_name='accepted_project', verbose_name=_("Linked Proposal"))
    research_file = models.FileField(_("Research File"), upload_to='research_files/', blank=True, null=True)
    show_research_to_students = models.BooleanField(_("Show Research to Students"), default=False)
    supervisor = models.ForeignKey('users.Supervisor', on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name=_("Supervisor"))
    coordinator = models.ForeignKey('users.Coordinator', on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name=_("Coordinator"))

    def __str__(self):
        return self.name


class ProjectPlan(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='plan', verbose_name=_("Project"))
    completion_status = models.IntegerField(_("Completion Status"), blank=True, null=True)


class ProjectGoal(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='goals', verbose_name=_("Project"))
    goal = models.TextField(_("Goal"), blank=True, null=True)
    duration = models.IntegerField(_("Goal Duration (Days)"), blank=True, null=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.goal} (Project: {self.project.name})"


class ProjectTask(models.Model):
    STATUS_CHOICES = [
        ('to do', _('To Do')),
        ('in progress', _('In Progress')),
        ('done', _('Done')),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name=_("Project"))
    goal = models.ForeignKey(ProjectGoal, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True, verbose_name=_("Goal"))
    name = models.CharField(_("Task Name"), max_length=255)
    outputs = models.TextField(_("Outputs"), blank=True)
    goals = models.TextField(_("Goals"), blank=True)
    remaining_tasks = models.TextField(_("Remaining Tasks"), blank=True)
    deliverable_text = models.TextField(_("Deliverable Text"), blank=True, null=True)
    deliverable_file = models.FileField(_("Deliverable File"), upload_to='task_deliverables/', blank=True, null=True)
    deadline_days = models.PositiveIntegerField(_("Deadline (Days)"), blank=True, null=True)
    assign_to = models.ForeignKey('users.Student', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks', verbose_name=_("Assigned To"))
    task_status = models.CharField(_("Task Status"), max_length=20, choices=STATUS_CHOICES, default='to do')
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)


class ProjectLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='logs', verbose_name=_("Project"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='project_logs', verbose_name=_("User"))
    message = models.TextField(_("Message"))
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)
    log_type = models.CharField(_("Log Type"), max_length=100, blank=True, null=True)
    attachment = models.FileField(_("Attachment"), upload_to='log_attachments/', null=True, blank=True)


class ProjectMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships', verbose_name=_("Project"))
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name=_("Role"))
    group_id = models.CharField(_("Group ID"), max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ['user', 'project', 'role']
        verbose_name = _("Project Membership")
        verbose_name_plural = _("Project Memberships")


class StudentProjectMembership(models.Model):
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, null=True, blank=True, related_name='project_membership', verbose_name=_("Student"))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='student_memberships', null=True, blank=True, verbose_name=_("Project"))
    proposal = models.ForeignKey(ProjectProposal, on_delete=models.CASCADE, related_name='student_proposal_memberships', null=True, blank=True, verbose_name=_("Proposal"))
    group_id = models.CharField(_("Group ID"), max_length=50, blank=True, null=True)


class AnnualGrade(models.Model):
    supervisor = models.ForeignKey('users.Supervisor', on_delete=models.CASCADE, related_name="supervised_annual_grades", verbose_name=_("Supervisor"))
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_annual_grades", verbose_name=_("Student"))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="annual_grades", verbose_name=_("Project"))
    grade = models.FloatField(_("Grade"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        unique_together = ("supervisor", "student", "project")
        verbose_name = _("Annual Grade")
        verbose_name_plural = _("Annual Grades")


class FeedbackExchange(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback_exchanges', verbose_name=_("Project"))
    proposal = models.ForeignKey(ProjectProposal, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback_exchanges', verbose_name=_("Proposal"))
    task = models.ForeignKey('ProjectTask', on_delete=models.CASCADE, null=True, blank=True, related_name='feedback_exchanges', verbose_name=_("Task"))
    report = models.ForeignKey('report.ProjectReport', on_delete=models.CASCADE, null=True, blank=True, related_name='feedback_exchanges', verbose_name=_("Report"))
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_feedbacks', verbose_name=_("Sender"))
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback_received', verbose_name=_("Receiver"))
    feedback_text = models.TextField(_("Feedback Text"), blank=True, null=True)
    feedback_file = models.FileField(_("Feedback File"), upload_to='feedback_files/', blank=True, null=True)
    comment = models.TextField(_("Comment"), blank=True, null=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
