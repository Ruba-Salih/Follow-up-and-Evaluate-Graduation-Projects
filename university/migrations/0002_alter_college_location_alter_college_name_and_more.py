

from django.db import migrations, models
import django.db.models.deletion



class Migration(migrations.Migration):

    dependencies = [
        ('university', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='college',
            name='location',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='college',
            name='name',
            field=models.CharField(max_length=200, verbose_name='College Name'),
        ),
        migrations.AlterField(
            model_name='college',
            name='university',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='colleges', to='university.university', verbose_name='University'),
        ),
        migrations.AlterField(
            model_name='department',
            name='college',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departments', to='university.college', verbose_name='College'),
        ),
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Department Name'),
        ),
        migrations.AlterField(
            model_name='university',
            name='name',
            field=models.CharField(max_length=200, verbose_name='University Name'),
        ),
    ]
