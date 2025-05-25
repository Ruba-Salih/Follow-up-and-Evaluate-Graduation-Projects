
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion



class Migration(migrations.Migration):

    dependencies = [
        ('university', '0002_alter_college_location_alter_college_name_and_more'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coordinator',
            name='coord_id',
            field=models.CharField(blank=True, default='', max_length=20, unique=True, verbose_name='Coordinator ID'),
        ),
        migrations.AlterField(
            model_name='coordinator',
            name='is_super',
            field=models.BooleanField(default=False, verbose_name='Is Super Coordinator?'),
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='Role Name'),
        ),
        migrations.AlterField(
            model_name='student',
            name='sitting_number',
            field=models.CharField(max_length=20, verbose_name='Sitting Number'),
        ),
        migrations.AlterField(
            model_name='student',
            name='student_id',
            field=models.CharField(max_length=20, unique=True, verbose_name='Student ID'),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='qualification',
            field=models.CharField(max_length=100, verbose_name='Qualification'),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='supervisor_id',
            field=models.CharField(max_length=20, unique=True, verbose_name='Supervisor ID'),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='total_projects',
            field=models.IntegerField(default=0, verbose_name='Total Projects'),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='work_place',
            field=models.CharField(max_length=100, verbose_name='Workplace'),
        ),
        migrations.AlterField(
            model_name='user',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='university.department', verbose_name='Department'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='usercreationlog',
            name='added_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Added At'),
        ),
        migrations.AlterField(
            model_name='usercreationlog',
            name='added_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='added_users', to='users.coordinator', verbose_name='Added By'),
        ),
        migrations.AlterField(
            model_name='usercreationlog',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='creation_log', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
