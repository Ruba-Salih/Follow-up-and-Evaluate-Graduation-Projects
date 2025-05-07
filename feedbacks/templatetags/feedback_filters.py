from django import template
from users.services import is_teacher
from project .models import StudentProjectMembership

register = template.Library()

@register.filter
def is_teacher_filter(user):
    return is_teacher(user)

@register.filter
def is_project_member(project, user):
    return StudentProjectMembership.objects.filter(project=project, student=user).exists()