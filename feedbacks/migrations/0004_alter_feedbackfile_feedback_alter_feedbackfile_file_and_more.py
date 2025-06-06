
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion



class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0004_feedbackexchange_task'),
        ('feedbacks', '0003_initial'),
      
        ('project', '0005_alter_annualgrade_options_and_more'),
      
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackfile',
            name='feedback',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='feedbacks.projectfeedback', verbose_name='Feedback'),
        ),
        migrations.AlterField(
            model_name='feedbackfile',
            name='file',
            field=models.FileField(upload_to='feedback_files/', verbose_name='File'),
        ),
        migrations.AlterField(
            model_name='feedbackfile',
            name='reply',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='feedbacks.feedbackreply', verbose_name='Reply'),
        ),
        migrations.AlterField(
            model_name='feedbackfile',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Uploaded At'),
        ),
        migrations.AlterField(
            model_name='feedbackreply',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='feedbackreply',
            name='feedback',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='reply', to='feedbacks.projectfeedback', verbose_name='Original Feedback'),
        ),
        migrations.AlterField(
            model_name='feedbackreply',
            name='message',
            field=models.TextField(blank=True, null=True, verbose_name='Reply Message'),
        ),
        migrations.AlterField(
            model_name='projectfeedback',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='projectfeedback',
            name='message',
            field=models.TextField(blank=True, null=True, verbose_name='Message'),
        ),
        migrations.AlterField(
            model_name='projectfeedback',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='projectfeedback',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_project_feedbacks', to=settings.AUTH_USER_MODEL, verbose_name='Sender'),
        ),
        migrations.AlterField(
            model_name='projectfeedback',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_project_feedbacks', to=settings.AUTH_USER_MODEL, verbose_name='Receiver (Teacher)'),
        ),
        migrations.AlterField(
            model_name='projectfeedback',
            name='title',
            field=models.CharField(blank=True, max_length=255, verbose_name='Title'),
        ),
    ]
