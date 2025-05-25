
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion



class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('form', '0003_alter_evaluationform_coordinators_and_more'),
        ('project', '0004_feedbackexchange_task'),
        ('users', '0002_alter_coordinator_coord_id_and_more'),
        ('grades', '0002_initial'),
        ('project', '0005_alter_annualgrade_options_and_more'),
        
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membergrade',
            options={'verbose_name': 'Member Grade', 'verbose_name_plural': 'Member Grades'},
        ),
        migrations.AlterModelOptions(
            name='memberindividualgrade',
            options={'verbose_name': 'Member Individual Grade', 'verbose_name_plural': 'Member Individual Grades'},
        ),
        migrations.AlterField(
            model_name='grade',
            name='evaluation_form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='form.evaluationform', verbose_name='Evaluation Form'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='final_grade',
            field=models.FloatField(verbose_name='Final Grade'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='grade',
            field=models.FloatField(verbose_name='Raw Grade'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='main_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='form.maincategory', verbose_name='Main Category'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='grading',
            name='final_grade',
            field=models.FloatField(verbose_name='Final Grade'),
        ),
        migrations.AlterField(
            model_name='grading',
            name='is_sent',
            field=models.BooleanField(default=False, verbose_name='Is Sent'),
        ),
        migrations.AlterField(
            model_name='grading',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='gradings', to='project.project', verbose_name='Project'),
        ),
        migrations.AlterField(
            model_name='grading',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gradings', to='users.student', verbose_name='Student'),
        ),
        migrations.AlterField(
            model_name='individualgrade',
            name='evaluation_form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individual_grades', to='form.evaluationform', verbose_name='Evaluation Form'),
        ),
        migrations.AlterField(
            model_name='individualgrade',
            name='final_grade',
            field=models.FloatField(verbose_name='Final Individual Grade'),
        ),
        migrations.AlterField(
            model_name='individualgrade',
            name='grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individual_grades', to='grades.grade', verbose_name='Overall Grade'),
        ),
        migrations.AlterField(
            model_name='individualgrade',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individual_grades', to='users.student', verbose_name='Student'),
        ),
        migrations.AlterField(
            model_name='membergrade',
            name='grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='grades.grade', verbose_name='Grade'),
        ),
        migrations.AlterField(
            model_name='membergrade',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='graded_projects', to=settings.AUTH_USER_MODEL, verbose_name='Member'),
        ),
        migrations.AlterField(
            model_name='memberindividualgrade',
            name='individual_grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluators', to='grades.individualgrade', verbose_name='Individual Grade'),
        ),
        migrations.AlterField(
            model_name='memberindividualgrade',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individual_graded_projects', to=settings.AUTH_USER_MODEL, verbose_name='Member'),
        ),
    ]
