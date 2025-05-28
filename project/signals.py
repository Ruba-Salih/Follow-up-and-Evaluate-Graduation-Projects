from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProjectProposal, Project, ProjectPlan, StudentProjectMembership, ProjectMembership, AnnualGrade
from users.models import Coordinator, Supervisor, Student, Role
from .services import assign_project_memberships
from .serializers import get_academic_year
from django.utils.crypto import get_random_string

@receiver(post_save, sender=ProjectProposal)
def create_project_from_proposal(sender, instance, created, **kwargs):
    if Project.objects.filter(proposal=instance).exists():
        return

    submitted_by = instance.submitted_by
    is_student_proposal = hasattr(submitted_by, 'student')
    is_teacher_proposal = not is_student_proposal

    supervisor_user = None
    coordinator = None
    duration = instance.duration or 0
    team_count = instance.team_member_count or instance.team_members.count()
    project = None

    if is_student_proposal:
        if instance.coordinator_status == 'accepted':
            if instance.teacher_status == 'accepted':
                supervisor_user = instance.proposed_to

   
                if supervisor_user and not hasattr(supervisor_user, 'supervisor'):
                    Supervisor.objects.create(
                        id=supervisor_user.id,  # Important: ensure same primary key
                        username=supervisor_user.username,
                        email=supervisor_user.email,
                        first_name=supervisor_user.first_name,
                        last_name=supervisor_user.last_name,
                        password=supervisor_user.password,
                        department=supervisor_user.department,
                        qualification="N/A",  # or collect real data if available
                        work_place="N/A",
                        supervisor_id=f"S{get_random_string(6)}",  # or any unique logic
                    )


            if submitted_by.student.department:
                coordinator = Coordinator.objects.filter(
                    department=submitted_by.student.department,
                    is_super=False
                ).first()

            project = Project.objects.create(
                name=instance.title,
                description=instance.description,
                proposal=instance,
                field=instance.field,
                department=instance.department,
                supervisor=supervisor_user.supervisor if supervisor_user else None,
                coordinator=coordinator,
                academic_year=get_academic_year(),
                team_member_count=team_count,
                duration=duration
            )

    elif is_teacher_proposal:
        if instance.coordinator_status == 'accepted':
            supervisor_user = submitted_by  # 💡 teacher becomes supervisor

            if instance.department:
                coordinator = Coordinator.objects.filter(
                    department=instance.department,
                    is_super=False
                ).first()

            project = Project.objects.create(
                name=instance.title,
                description=instance.description,
                proposal=instance,
                field=instance.field,
                department=instance.department,
                supervisor=getattr(supervisor_user, 'supervisor', None),
                coordinator=coordinator,
                academic_year=get_academic_year(),
                team_member_count=team_count,
                duration=duration
            )

    if project:
        member_payload = []

        if coordinator:
            member_payload.append({
                "user_id": coordinator.id,
                "role": "Coordinator",
                "group_id": None
            })

        if supervisor_user:
            selected_role = instance.teacher_role.name if instance.teacher_role else "Supervisor"
            member_payload.append({
                "user_id": supervisor_user.id,
                "role": selected_role,
                "group_id": None
            })


        assign_project_memberships(project, member_payload)


@receiver(post_save, sender=Project)
def setup_project_relations(sender, instance, created, **kwargs):
    if not created:
        return

    ProjectPlan.objects.create(project=instance)

    proposal = instance.proposal
    if proposal:
        if hasattr(proposal.submitted_by, "student"):
            StudentProjectMembership.objects.get_or_create(
                student=proposal.submitted_by.student,
                project=instance
            )
        for student in proposal.team_members.all():
            StudentProjectMembership.objects.get_or_create(
                student=student,
                project=instance
            )

        if instance.supervisor:
            all_students = [proposal.submitted_by] + list(proposal.team_members.all())
            for user in all_students:
                if hasattr(user, "student"):
                    AnnualGrade.objects.get_or_create(
                        student=user.student,
                        supervisor=instance.supervisor,
                        project=instance,
                        defaults={"grade": 0.0}
                    )
    StudentProjectMembership.objects.filter(proposal=proposal).exclude(project=instance).delete()

