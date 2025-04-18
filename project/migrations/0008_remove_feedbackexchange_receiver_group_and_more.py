# Generated by Django 5.1.7 on 2025-03-21 19:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_feedbackexchange'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedbackexchange',
            name='receiver_group',
        ),
        migrations.RemoveField(
            model_name='feedbackexchange',
            name='receiver_user',
        ),
        migrations.AddField(
            model_name='feedbackexchange',
            name='receiver',
            field=models.ForeignKey(blank=True, help_text='The receiver of the feedback. If left blank, feedback is sent to all students in the project.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedback_received', to=settings.AUTH_USER_MODEL),
        ),
    ]
