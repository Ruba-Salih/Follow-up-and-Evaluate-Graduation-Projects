
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion



class Migration(migrations.Migration):

    dependencies = [
        ('report', '0003_projectreport_teammemberstatus_and_more'),
        ('users', '0002_alter_coordinator_coord_id_and_more'),
        ('university', '0002_alter_college_location_alter_college_name_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0004_feedbackexchange_task'),

    ]

    operations = [
        migrations.AlterModelOptions(
            name='annualgrade',
            options={'verbose_name': 'Annual Grade', 'verbose_name_plural': 'Annual Grades'},
        ),
        migrations.AlterModelOptions(
            name='projectmembership',
            options={'verbose_name': 'Project Membership', 'verbose_name_plural': 'Project Memberships'},
        ),

        migrations.AddField(
            model_name='feedbackexchange',
            name='report',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedback_exchanges', to='report.projectreport', verbose_name='Report'),
        ),
        migrations.AlterField(
            model_name='annualgrade',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='annualgrade',
            name='grade',
            field=models.FloatField(verbose_name='Grade'),
        ),
        migrations.AlterField(
            model_name='annualgrade',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annual_grades', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='annualgrade',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_annual_grades', to=settings.AUTH_USER_MODEL, verbose_name='Student'),
        ),
        migrations.AlterField(
            model_name='annualgrade',
            name='supervisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervised_annual_grades', to='users.supervisor', verbose_name='Supervisor'),
        ),
        migrations.AlterField(
            model_name='feedbackexchange',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Comment'),
        ),
        migrations.AlterField(
            model_name='feedbackexchange',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='feedbackexchange',
            name='feedback_file',
            field=models.FileField(blank=True, null=True, upload_to='feedback_files/', verbose_name='Feedback File'),
        ),
        migrations.AlterField(
            model_name='feedbackexchange',
            name='feedback_text',
            field=models.TextField(blank=True, null=True, verbose_name='Feedback Text'),
        ),
        migrations.AlterField(
            model_name='feedbackexchange',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedback_exchanges', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='feedbackexchange',
            name='proposal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedback_exchanges', to='project.projectproposal', verbose_name='Proposal'),
        ),
        migrations.AlterField(
            model_name='feedbackexchange',
            name='receiver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedback_received', to=settings.AUTH_USER_MODEL, verbose_name='Receiver'),
        ),
        migrations.AlterField(
            model_name='feedbackexchange',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_feedbacks', to=settings.AUTH_USER_MODEL, verbose_name='Sender'),
        ),
        migrations.AlterField(
            model_name='feedbackexchange',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedback_exchanges', to='project.projecttask', verbose_name='Task'),
        ),
        migrations.AlterField(
            model_name='project',
            name='academic_year',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Academic Year'),
        ),
        migrations.AlterField(
            model_name='project',
            name='coordinator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects', to='users.coordinator', verbose_name='Coordinator'),
        ),
        migrations.AlterField(
            model_name='project',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='university.department', verbose_name='Department'),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='project',
            name='duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Duration (Days)'),
        ),
        migrations.AlterField(
            model_name='project',
            name='field',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Field'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Project Name'),
        ),
        migrations.AlterField(
            model_name='project',
            name='proposal',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accepted_project', to='project.projectproposal', verbose_name='Linked Proposal'),
        ),
        migrations.AlterField(
            model_name='project',
            name='research_file',
            field=models.FileField(blank=True, null=True, upload_to='research_files/', verbose_name='Research File'),
        ),
        migrations.AlterField(
            model_name='project',
            name='show_research_to_students',
            field=models.BooleanField(default=False, verbose_name='Show Research to Students'),
        ),
        migrations.AlterField(
            model_name='project',
            name='supervisor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects', to='users.supervisor', verbose_name='Supervisor'),
        ),
        migrations.AlterField(
            model_name='project',
            name='team_member_count',
            field=models.IntegerField(null=True, verbose_name='Team Member Count'),
        ),
        migrations.AlterField(
            model_name='projectgoal',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='projectgoal',
            name='duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Goal Duration (Days)'),
        ),
        migrations.AlterField(
            model_name='projectgoal',
            name='goal',
            field=models.TextField(blank=True, null=True, verbose_name='Goal'),
        ),
        migrations.AlterField(
            model_name='projectgoal',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='projectlog',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='log_attachments/', verbose_name='Attachment'),
        ),
        migrations.AlterField(
            model_name='projectlog',
            name='log_type',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Log Type'),
        ),
        migrations.AlterField(
            model_name='projectlog',
            name='message',
            field=models.TextField(verbose_name='Message'),
        ),
        migrations.AlterField(
            model_name='projectlog',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='projectlog',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Timestamp'),
        ),
        migrations.AlterField(
            model_name='projectlog',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_logs', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='projectmembership',
            name='group_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Group ID'),
        ),
        migrations.AlterField(
            model_name='projectmembership',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='projectmembership',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.role', verbose_name='Role'),
        ),
        migrations.AlterField(
            model_name='projectmembership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='projectplan',
            name='completion_status',
            field=models.IntegerField(blank=True, null=True, verbose_name='Completion Status'),
        ),
        migrations.AlterField(
            model_name='projectplan',
            name='project',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='plan', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='additional_comment',
            field=models.TextField(blank=True, null=True, verbose_name='Additional Comment'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='attached_file',
            field=models.FileField(blank=True, null=True, upload_to='project_proposals/', verbose_name='Attached File'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='coordinator_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20, verbose_name='Coordinator Status'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='university.department', verbose_name='Department'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Duration (Days)'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='field',
            field=models.CharField(max_length=200, verbose_name='Field'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='proposed_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='received_proposals', to=settings.AUTH_USER_MODEL, verbose_name='Proposed To'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='submitted_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_proposals', to=settings.AUTH_USER_MODEL, verbose_name='Submitted By'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='teacher_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20, verbose_name='Teacher Status'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='team_member_count',
            field=models.IntegerField(verbose_name='Team Member Count'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='team_members',
            field=models.ManyToManyField(blank=True, related_name='team_proposals', to='users.student', verbose_name='Team Members'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='assign_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to='users.student', verbose_name='Assigned To'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='deadline_days',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Deadline (Days)'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='deliverable_file',
            field=models.FileField(blank=True, null=True, upload_to='task_deliverables/', verbose_name='Deliverable File'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='deliverable_text',
            field=models.TextField(blank=True, null=True, verbose_name='Deliverable Text'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='goal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='project.projectgoal', verbose_name='Goal'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='goals',
            field=models.TextField(blank=True, verbose_name='Goals'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Task Name'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='outputs',
            field=models.TextField(blank=True, verbose_name='Outputs'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='remaining_tasks',
            field=models.TextField(blank=True, verbose_name='Remaining Tasks'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='task_status',
            field=models.CharField(choices=[('to do', 'To Do'), ('in progress', 'In Progress'), ('done', 'Done')], default='to do', max_length=20, verbose_name='Task Status'),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
        migrations.AlterField(
            model_name='studentprojectmembership',
            name='group_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Group ID'),
        ),
        migrations.AlterField(
            model_name='studentprojectmembership',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_memberships', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='studentprojectmembership',
            name='proposal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_proposal_memberships', to='project.projectproposal', verbose_name='Proposal'),
        ),
        migrations.AlterField(
            model_name='studentprojectmembership',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_membership', to='users.student', verbose_name='Student'),
        ),
    ]
