from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProjectProposal, Project

@receiver(post_save, sender=ProjectProposal)
def create_project_from_proposal(sender, instance, created, **kwargs):
    # If the proposal is accepted and no project has been created yet.
    if instance.status == 'accepted' and not hasattr(instance, 'accepted_project'):
        # Create a new Project instance using the proposal's data.
        project = Project.objects.create(
            name=instance.title,
            description=instance.description,
            proposal=instance,
            field=instance.field,         # 'field' from the proposal saved to the project
            department=instance.department  # 'department' from the proposal saved to the project
        )
