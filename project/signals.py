# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProjectProposal, Project
from users.models import Supervisor, Coordinator

@receiver(post_save, sender=ProjectProposal)
def create_project_from_proposal(sender, instance, created, **kwargs):
    if hasattr(instance, 'accepted_project'):
        return  # Prevent creating a duplicate project

    submitted_by = instance.submitted_by
    is_student_proposal = hasattr(submitted_by, 'student')
    is_teacher_proposal = not is_student_proposal

    if is_student_proposal:
        if instance.teacher_status == 'accepted' and instance.coordinator_status == 'accepted':
            Project.objects.create(
                name=instance.title,
                description=instance.description,
                proposal=instance,
                field=instance.field,
                department=str(instance.department),
                supervisor=instance.proposed_to.supervisor if hasattr(instance.proposed_to, 'supervisor') else None,
                coordinator=instance.proposed_to.coordinator if hasattr(instance.proposed_to, 'coordinator') else None,
            )
    elif is_teacher_proposal:
        if instance.coordinator_status == 'accepted':
            Project.objects.create(
                name=instance.title,
                description=instance.description,
                proposal=instance,
                field=instance.field,
                department=str(instance.department),
                supervisor=submitted_by.supervisor if hasattr(submitted_by, 'supervisor') else None,
                coordinator=instance.proposed_to.coordinator if hasattr(instance.proposed_to, 'coordinator') else None,
            )
