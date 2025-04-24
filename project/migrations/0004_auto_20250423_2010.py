from django.db import migrations

def map_department_strings(apps, schema_editor):
    Project = apps.get_model('project', 'Project')
    Department = apps.get_model('university', 'Department')

    for project in Project.objects.all():
        if isinstance(project.department, str) and project.department:
            try:
                dept = Department.objects.get(name__iexact=project.department.strip())
                project.department = dept
                project.save()
            except Department.DoesNotExist:
                print(f"[!] No Department found for: {project.department}")
                project.department = None
                project.save()

class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_initial'),  # Use correct previous migration
        ('university', '__latest__'),  # Ensure it can see Department
    ]

    operations = [
        migrations.RunPython(map_department_strings),
    ]
