from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProjectProposal, Project

@receiver(post_save, sender=ProjectProposal)
def create_project_from_proposal(sender, instance, created, **kwargs):
    # Check if the proposal is accepted and not yet linked to a Project.
    if instance.coordinator_status == 'accepted' and not hasattr(instance, 'accepted_project'):
        project = Project.objects.create(
            name=instance.title,
            description=instance.description,
            proposal=instance,
            field=instance.field,
            department=instance.department,
            supervisor=instance.proposed_to.supervisor if hasattr(instance.proposed_to, 'supervisor') else None,
            coordinator=instance.proposed_to.coordinator if hasattr(instance.proposed_to, 'coordinator') else None
        )
