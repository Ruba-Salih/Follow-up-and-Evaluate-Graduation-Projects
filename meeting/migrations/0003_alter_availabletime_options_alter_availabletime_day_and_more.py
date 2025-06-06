
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion



class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0004_feedbackexchange_task'),
        ('meeting', '0002_initial'),

        ('project', '0005_alter_annualgrade_options_and_more'),
    
    ]

    operations = [
        migrations.AlterModelOptions(
            name='availabletime',
            options={'verbose_name': 'Available Time', 'verbose_name_plural': 'Available Times'},
        ),
        migrations.AlterField(
            model_name='availabletime',
            name='day',
            field=models.CharField(choices=[('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'), ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday')], max_length=3, verbose_name='Day of Week'),
        ),
        migrations.AlterField(
            model_name='availabletime',
            name='end_time',
            field=models.TimeField(verbose_name='End Time'),
        ),
        migrations.AlterField(
            model_name='availabletime',
            name='start_time',
            field=models.TimeField(verbose_name='Start Time'),
        ),
        migrations.AlterField(
            model_name='availabletime',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='available_times', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='comment',
            field=models.TextField(blank=True, help_text='Message or agenda for the meeting', null=True, verbose_name='Comment'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='end_datetime',
            field=models.DateTimeField(verbose_name='End Time'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='meeting_report',
            field=models.TextField(blank=True, help_text='Filled by student after meeting is completed', null=True, verbose_name='Meeting Report'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='project',
            field=models.ForeignKey(blank=True, help_text='Linked project if applicable', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='meetings', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='recommendation',
            field=models.TextField(blank=True, help_text='Post-meeting notes or recommendations', null=True, verbose_name='Recommendation'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='requested_by',
            field=models.ForeignKey(help_text='User who requested the meeting', on_delete=django.db.models.deletion.CASCADE, related_name='requested_meetings', to=settings.AUTH_USER_MODEL, verbose_name='Requested By'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='start_datetime',
            field=models.DateTimeField(verbose_name='Start Time'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings_as_teacher', to=settings.AUTH_USER_MODEL, verbose_name='Teacher'),
        ),
        migrations.AlterField(
            model_name='meetingfile',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='meetingfile',
            name='file',
            field=models.FileField(upload_to='meeting_files/', verbose_name='File'),
        ),
        migrations.AlterField(
            model_name='meetingfile',
            name='meeting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='meeting.meeting', verbose_name='Meeting'),
        ),
        migrations.AlterField(
            model_name='meetingfile',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Uploaded At'),
        ),
        migrations.AlterField(
            model_name='meetingfile',
            name='uploaded_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meeting_files_uploaded', to=settings.AUTH_USER_MODEL, verbose_name='Uploaded By'),
        ),
        migrations.AlterField(
            model_name='meetingparticipant',
            name='attendance_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('attended', 'Attended'), ('absent', 'Absent')], default='pending', max_length=10, verbose_name='Attendance Status'),
        ),
        migrations.AlterField(
            model_name='meetingparticipant',
            name='has_accepted',
            field=models.BooleanField(default=False, verbose_name='Has Accepted'),
        ),
        migrations.AlterField(
            model_name='meetingparticipant',
            name='meeting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='meeting.meeting', verbose_name='Meeting'),
        ),
        migrations.AlterField(
            model_name='meetingparticipant',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meeting_participations', to=settings.AUTH_USER_MODEL, verbose_name='Participant'),
        ),
    ]
