from rest_framework import permissions, viewsets, status
from django.views import View
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from .models import Announcement, AnnouncementFile
from .serializers import AnnouncementSerializer
from university.models import Department
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseForbidden


User = get_user_model()


@method_decorator(login_required, name='dispatch')
class AnnouncementCreateView(View):
    def get(self, request):
        # Only coordinators allowed
        if not hasattr(request.user, 'coordinator'):
            return render(request, '403.html', status=403)

        departments = Department.objects.all()
        api_url = reverse('announcement-list')  # From DRF DefaultRouter

        return render(request, 'announcement/create_announcement.html',  {'departments': departments, 'api_url': api_url,})


def is_teacher(user):
    return not any([
        hasattr(user, 'student'),
        hasattr(user, 'coordinator'),
        hasattr(user, 'admin'),
        user.is_superuser,
    ])

class IsCoordinator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'coordinator')

class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsCoordinator]

    def get_queryset(self):
        # Coordinators see only their own announcements
        return Announcement.objects.filter(created_by=self.request.user)

    """ def perform_create(self, serializer):
        serializer.save(created_by=self.request.user) """

    def perform_create(self, serializer):
        announcement = serializer.save(created_by=self.request.user)

        for f in self.request.FILES.getlist('attachment'):
            AnnouncementFile.objects.create(
                announcement=announcement,
                file=f,
                uploaded_by=self.request.user
            )

    def get_recipients(self, announcement):
        """
        Returns a queryset of users who should receive this announcement,
        based on target_roles and target_departments.
        """
        users = User.objects.all()

        # Filter by departments if specified (if none selected, all departments)
        if announcement.target_departments.exists():
            users = users.filter(department__in=announcement.target_departments.all())

        filtered_users = []

        for user in users:
            for role in announcement.target_roles:
                if role == 'student' and hasattr(user, 'student'):
                    filtered_users.append(user)
                    break
                elif role == 'supervisor' and hasattr(user, 'supervisor'):
                    filtered_users.append(user)
                    break
                elif role == 'reader' and hasattr(user, 'reader'):
                    filtered_users.append(user)
                    break
                elif role == 'committee' and hasattr(user, 'Judgment Committee'):
                    filtered_users.append(user)
                    break
                elif role == 'teacher' and is_teacher(user):
                    filtered_users.append(user)
                    break

        return filtered_users


@login_required
def manage_announcements(request):
    # Only coordinators allowed
    if not hasattr(request.user, 'coordinator'):
        return HttpResponseForbidden("You are not authorized.")

    status_filter = request.GET.get('status')
    announcements = Announcement.objects.all()

    if status_filter == 'active':
        announcements = announcements.filter(is_active=True)
    elif status_filter == 'inactive':
        announcements = announcements.filter(is_active=False)

    announcements = announcements.order_by('-deadline')

    # Handle POST actions like delete, activate, deactivate here

    if request.method == 'POST':
        ann_id = request.POST.get('announcement_id')
        action = request.POST.get('action')
        try:
            announcement = announcements.get(id=ann_id)
        except Announcement.DoesNotExist:
            announcement = None

        if announcement:
            if action == 'delete':
                announcement.delete()
            elif action == 'activate':
                announcement.is_active = True
                announcement.save()
            elif action == 'deactivate':
                announcement.is_active = False
                announcement.save()

        return redirect('manage_announcements')  

    available_roles = [r[0] for r in Announcement.ROLE_CHOICES]
    from university.models import Department
    all_departments = Department.objects.all()

    return render(request, 'announcement/manage_expired.html', {
        'expired_announcements': announcements,
        'available_roles': available_roles,      # ✅ Added
        'all_departments': all_departments,      # ✅ Added
    })


@login_required
def announcement_edit(request, announcement_id):
    if not hasattr(request.user, 'coordinator'):
        return HttpResponseForbidden("You are not authorized.")
    
    announcement = get_object_or_404(Announcement, id=announcement_id)

    if announcement.created_by != request.user:
        return HttpResponseForbidden("You are not authorized.")

    # Fetch all departments for form display
    all_departments = Department.objects.all()

    # Your available roles as defined in Announcement model ROLE_CHOICES
    available_roles = [role[0] for role in Announcement.ROLE_CHOICES]

    print(f"departments are: {all_departments}, and roles are {available_roles}")
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        deadline_str = request.POST.get('deadline')
        is_active_str = request.POST.get('is_active')

        if not title:
            # You might want to add error handling instead of redirect
            return redirect('manage_announcements')

        announcement.title = title
        announcement.message = message

        if deadline_str:
            try:
                announcement.deadline = timezone.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
                announcement.deadline = timezone.make_aware(announcement.deadline)
            except ValueError:
                announcement.deadline = None
        else:
            announcement.deadline = None

        announcement.is_active = (is_active_str == 'true')

        # Update target_roles from submitted data: this should be a list of role strings
        selected_roles = request.POST.getlist('target_roles')
        # Validate roles (optional)
        valid_roles = [r for r in selected_roles if r in available_roles]
        announcement.target_roles = valid_roles

        announcement.save()

        # Update target_departments (many-to-many)
        selected_dept_ids = request.POST.getlist('target_departments')
        if selected_dept_ids:
            # Clear existing and add new ones
            announcement.target_departments.set(selected_dept_ids)
        else:
            # If none selected, clear all (means all departments targeted)
            announcement.target_departments.clear()

        # Remove selected files
        remove_files_ids = request.POST.getlist('remove_files')
        for file_id in remove_files_ids:
            try:
                file_obj = AnnouncementFile.objects.get(id=file_id, announcement=announcement)
                file_obj.file.delete(save=False)  # Remove from storage
                file_obj.delete()  # Remove DB record
            except AnnouncementFile.DoesNotExist:
                pass

        # Add new uploaded files, assign uploaded_by
        new_files = request.FILES.getlist('new_files')
        for f in new_files:
            AnnouncementFile.objects.create(
                announcement=announcement,
                file=f,
                uploaded_by=request.user
            )

        return redirect('manage_announcements')

    # GET: Render edit form with current announcement data
    context = {
        'announcement': announcement,
        'all_departments': all_departments,
        'available_roles': available_roles,
    }
    return render(request, 'announcement/edit_announcement.html', context)