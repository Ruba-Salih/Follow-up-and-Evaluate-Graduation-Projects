# Generated by Django 4.2.19 on 2025-05-10 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_project_research_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedbackexchange',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedback_exchanges', to='project.projecttask'),
        ),
    ]
