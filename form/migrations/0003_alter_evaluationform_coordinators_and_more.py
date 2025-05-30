
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_coordinator_coord_id_and_more'),
        ('form', '0002_initial'),

    ]

    operations = [
        migrations.AlterField(
            model_name='evaluationform',
            name='coordinators',
            field=models.ManyToManyField(blank=True, related_name='evaluation_forms', to='users.coordinator', verbose_name='Coordinators'),
        ),
        migrations.AlterField(
            model_name='evaluationform',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='evaluationform',
            name='form_weight',
            field=models.FloatField(help_text='The weight of the entire evaluation form.', verbose_name='Form Weight'),
        ),
        migrations.AlterField(
            model_name='evaluationform',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Form Name'),
        ),
        migrations.AlterField(
            model_name='evaluationform',
            name='target_role',
            field=models.ForeignKey(blank=True, help_text='The role of users for whom this evaluation form is intended.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.role', verbose_name='Target Role'),
        ),
        migrations.AlterField(
            model_name='maincategory',
            name='evaluation_form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='main_categories', to='form.evaluationform', verbose_name='Evaluation Form'),
        ),
        migrations.AlterField(
            model_name='maincategory',
            name='grade_type',
            field=models.CharField(choices=[('individual', 'Individual Grade'), ('group', 'Group Grade')], max_length=20, verbose_name='Grade Type'),
        ),
        migrations.AlterField(
            model_name='maincategory',
            name='number',
            field=models.PositiveIntegerField(verbose_name='Number'),
        ),
        migrations.AlterField(
            model_name='maincategory',
            name='text',
            field=models.TextField(verbose_name='Category Text'),
        ),
        migrations.AlterField(
            model_name='maincategory',
            name='weight',
            field=models.FloatField(verbose_name='Category Weight'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='main_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_categories', to='form.maincategory', verbose_name='Main Category'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='text',
            field=models.TextField(verbose_name='Subcategory Text'),
        ),
    ]
