from .models import ProjectGoal, ProjectMembership, ProjectTask
from users.models import Role
from django.db.models import Count, Q
from rest_framework.exceptions import ValidationError

def validate_student_limit(data, is_proposal=True):
    count_field = "team_member_count"
    team_field = "team_members_ids" if is_proposal else "student_ids"

    max_count = int(data.get(count_field) or 0)
    selected = data.getlist(team_field) if hasattr(data, "getlist") else data.get(team_field, [])

    if not isinstance(selected, list):
        selected = [selected]

    if max_count and len(selected) > max_count:
        raise ValidationError({
            team_field: [f"Cannot select more than {max_count} team member(s)."]
        })

    return True


def get_role_name_from_id(role_id):
    return {
        1: "Supervisor",
        2: "Reader",
        3: "Judgement Committee",
        4: "Coordinator"
    }.get(role_id)

def assign_project_memberships(project, members):
    for member in members:
        print(f"🔍 Handling member: {member}")
        if not member.get("user_id"):
            print("⚠️ Missing user_id, skipping member.")
            continue

        role_value = member.get("role")
        if not role_value:
            print("⚠️ Missing role, skipping member.")
            continue

        # Normalize role name
        if isinstance(role_value, int):
            role_name = get_role_name_from_id(role_value)
        else:
            role_name = str(role_value).strip().capitalize()

        if not role_name:
            print(f"⚠️ Invalid role ID or name: '{role_value}', skipping.")
            continue

        # Check role exists in DB
        role_obj = Role.objects.filter(name__iexact=role_name).first()
        if not role_obj:
            
            continue

        # Debug log before creation
        print(f"✅ Assigning {role_name} to user {member['user_id']} in project {project.id}")

        # Assign membership
        ProjectMembership.objects.create(
        user_id=member["user_id"],
        project=project,
        role=role_obj,
        group_id=member.get("group_id")
        )


def calculate_completion_by_tasks(project):
    tasks = ProjectTask.objects.filter(project=project)
    total = tasks.count()
    done = tasks.filter(task_status="done").count()
    return (done / total) * 100 if total > 0 else 0

def calculate_completion_by_goals(project):
    goals = ProjectGoal.objects.filter(project=project).annotate(
        total_tasks=Count("tasks"),
        done_tasks=Count("tasks", filter=Q(tasks__task_status="done"))
    )

    if not goals.exists():
        return 0

    total_completion = 0
    for g in goals:
        if g.total_tasks > 0:
            total_completion += (g.done_tasks / g.total_tasks) * 100

    return total_completion / goals.count()
