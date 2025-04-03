from django.db import migrations

def create_default_hierarchy(apps, schema_editor):
    University = apps.get_model('university', 'University')
    College = apps.get_model('university', 'College')
    Department = apps.get_model('university', 'Department')
    User = apps.get_model('users', 'User')

    # Create default University if not exists
    default_uni, created = University.objects.get_or_create(
        name="Sudan University of Science and Technology"
    )

    # Create default College for that university
    default_college, created = College.objects.get_or_create(
        name="Computer Science and Information Technology",
        university=default_uni,
        defaults={'location': 'Khartoum_Sudan'}
    )

    # Create default Department for that college
    default_dept, created = Department.objects.get_or_create(
        name="Software Engineering",
        college=default_college
    )

    # Assign default department to all users with no department set
    for user in User.objects.filter(department__isnull=True):
        user.department = default_dept
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('university', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_hierarchy),
    ]
