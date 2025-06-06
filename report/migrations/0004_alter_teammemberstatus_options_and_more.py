
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone



class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0005_alter_annualgrade_options_and_more'),
        ('users', '0002_alter_coordinator_coord_id_and_more'),
        ('report', '0003_projectreport_teammemberstatus_and_more'),

    ]

    operations = [
        migrations.AlterModelOptions(
            name='teammemberstatus',
            options={'verbose_name': 'Team Member Status', 'verbose_name_plural': 'Team Member Statuses'},
        ),
        migrations.AlterField(
            model_name='projectreport',
            name='challenges',
            field=models.TextField(blank=True, null=True, verbose_name='Challenges'),
        ),
        migrations.AlterField(
            model_name='projectreport',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='projectreport',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
        migrations.AlterField(
            model_name='projectreport',
            name='progress',
            field=models.TextField(blank=True, null=True, verbose_name='Progress'),
        ),
        migrations.AlterField(
            model_name='projectreport',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_reports', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='projectreport',
            name='report_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Report Date'),
        ),
        migrations.AlterField(
            model_name='projectreport',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
        migrations.AlterField(
            model_name='projectreport',
            name='work_done',
            field=models.TextField(blank=True, null=True, verbose_name='Work Done'),
        ),
        migrations.AlterField(
            model_name='projectreport',
            name='work_remaining',
            field=models.TextField(blank=True, null=True, verbose_name='Work Remaining'),
        ),
        migrations.AlterField(
            model_name='teammemberstatus',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='teammemberstatus',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_statuses', to='report.projectreport', verbose_name='Report'),
        ),
        migrations.AlterField(
            model_name='teammemberstatus',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='teammemberstatus',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.student', verbose_name='Student'),
        ),
    ]
