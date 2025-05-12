from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from project.serializers import ProjectProposalSerializer, ProjectSerializer
from users.models import Coordinator, Student
from users.serializers import StudentSerializer
from users.services import is_teacher
from .models import ProjectReport
from .serializers import ProjectReportSerializer
from project.models import Project, ProjectMembership, ProjectProposal, StudentProjectMembership
from feedbacks.models import ProjectFeedback
from users.models import User


@login_required
def track_projects_view(request):
    user = request.user
    is_super_coord = hasattr(user, 'coordinator') and user.coordinator.is_super

    reports_qs = ProjectReport.objects.select_related("project", "created_by").prefetch_related("member_statuses__student").order_by("-report_date")
    if hasattr(user, 'coordinator') and not is_super_coord:
        user_department = user.coordinator.department
        reports_qs = reports_qs.filter(project__department=user_department)

    report_data = []
    for report in reports_qs:
        students = [
            {
                "name": f"{s.student.first_name} {s.student.last_name}",
                "username": s.student.username,
                "status": s.status
            }
            for s in report.member_statuses.all()
        ]

        report_data.append({
            "id": report.id,
            "project_name": report.project.name,
            "supervisor": report.created_by.get_full_name() or report.created_by.username,
            "report_date": report.report_date.strftime("%Y-%m-%d"),
            "progress": report.progress,
            "work_done": report.work_done,
            "work_remaining": report.work_remaining,
            "challenges": report.challenges,
            "students": students  # ← plain Python list
        })

    return render(request, 'project/track_project.html', {
        "is_super_coord": is_super_coord,
        "reports": report_data
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_project_students(request, project_id):
    if not is_supervisor(request.user):
        return Response({"detail": "Not authorized."}, status=403)

    members = StudentProjectMembership.objects.filter(project_id=project_id).select_related("student")
    data = [
        {
            "id": m.student.id,
            "username": m.student.username,
            "first_name": m.student.first_name,
            "last_name": m.student.last_name,
            "role": "Student"
        }
        for m in members if m.student
    ]
    return Response({"members": data})

def is_supervisor(user):
    return ProjectMembership.objects.filter(user=user, role__name="Supervisor").exists()


@login_required
def supervisor_reports_page(request, project_id):
    if not is_supervisor(request.user):
        return HttpResponseForbidden("Access denied. Not a supervisor.")

    is_assigned = ProjectMembership.objects.filter(
        user=request.user,
        role__name="Supervisor",
        project_id=project_id
    ).exists()

    if not is_assigned:
        return HttpResponseForbidden("You are not assigned to this project.")

    project = get_object_or_404(Project, pk=project_id)

    reports = ProjectReport.objects.filter(
        project=project,
        created_by=request.user
    ).order_by("-report_date")

    feedbacks = ProjectFeedback.objects.filter(project=project).order_by("-created_at")

    return render(request, "reports/supervisor_reports.html", {
        "supervisor": request.user,
        "project_id": project.id,
        "project_name": project.name,
        "reports": reports,
        "feedbacks": feedbacks,
    })


class ProjectReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if not is_supervisor(request.user):
            return Response({"detail": "Only supervisors can view reports."}, status=403)

        if pk:
            report = get_object_or_404(ProjectReport, pk=pk, created_by=request.user)
            serializer = ProjectReportSerializer(report)
            return Response(serializer.data)

        reports = ProjectReport.objects.filter(created_by=request.user).order_by("-report_date")
        serializer = ProjectReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not is_supervisor(request.user):
            return Response({"detail": "Only supervisors can submit reports."}, status=403)

        data = request.data.copy()
        data["report_date"] = timezone.now().date()

        serializer = ProjectReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def put(self, request, pk):
        if not is_supervisor(request.user):
            return Response({"detail": "Only supervisors can edit reports."}, status=403)

        report = get_object_or_404(ProjectReport, pk=pk, created_by=request.user)
        serializer = ProjectReportSerializer(report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        if not is_supervisor(request.user):
            return Response({"detail": "Only supervisors can delete reports."}, status=403)

        report = get_object_or_404(ProjectReport, pk=pk, created_by=request.user)
        report.delete()
        return Response({"detail": "Report deleted successfully."}, status=204)


@login_required
def manege_reports(request):
    return render(request, 'reports/coord_reports.html')

@login_required
def report_projects_view(request):
    return render(request, 'reports/report_projects.html')

@login_required
def report_unassigned_students_view(request):
    return render(request, 'reports/report_unassigned_students.html')

@login_required
def report_teacher_roles_view(request):
    return render(request, 'reports/report_teacher_roles.html')

@login_required
def report_proposals_view(request):
    return render(request, 'reports/report_proposals.html')

@login_required
def report_projects_by_coord_view(request):
    return render(request, 'reports/report_projects_by_coordinator.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_view(request):
    user = request.user
    view_type = request.query_params.get("type")

    if view_type == "projects":
        projects = Project.objects.prefetch_related(
            "memberships__user", "memberships__role", "student_memberships__student"
        ).select_related("department")

        if hasattr(user, "coordinator") and not user.coordinator.is_super:
            projects = projects.filter(department=user.coordinator.department)

        projects = projects.order_by("-id")
        result = []

        for project in projects:
            supervisor_membership = next(
                (m for m in project.memberships.all() if m.role.name == "Supervisor"), None
            )

            result.append({
                "id": project.id,
                "name": project.name,
                "field": {"name": project.field} if project.field else None,
                "department": {"name": project.department.name} if project.department else None,
                "supervisor": {
                    "username": supervisor_membership.user.username,
                    "full_name": f"{supervisor_membership.user.first_name} {supervisor_membership.user.last_name}".strip()
                } if supervisor_membership else None,
                "team_members": [
                    {
                        "username": spm.student.username,
                        "full_name": f"{spm.student.first_name} {spm.student.last_name}".strip()
                    }
                    for spm in project.student_memberships.all() if spm.student
                ],
            })

        return Response(result)

    elif view_type == "non_assigned_students":
        assigned_ids = StudentProjectMembership.objects.values_list("student_id", flat=True)
        students = Student.objects.select_related("department").exclude(id__in=assigned_ids)

        if hasattr(user, "coordinator") and not user.coordinator.is_super:
            students = students.filter(department=user.coordinator.department)

        data = [
            {
                "student_id": s.student_id,
                "first_name": s.first_name,
                "last_name": s.last_name,
                "department": s.department.name if s.department else "—"
            }
            for s in students
        ]
        return Response(data)

    elif view_type == "teacher_roles":
        all_teachers = [u for u in User.objects.all() if is_teacher(u)]

        # Limit to department if normal coordinator
        if hasattr(user, "coordinator") and not user.coordinator.is_super:
            all_teachers = [t for t in all_teachers if t.department == user.coordinator.department]

        memberships = ProjectMembership.objects.select_related("user", "role", "project", "project__department")
        teacher_project_map = {}

        for m in memberships:
            if is_teacher(m.user):
                if m.user.id not in teacher_project_map:
                    teacher_project_map[m.user.id] = []
                teacher_project_map[m.user.id].append({
                    "project": m.project.name,
                    "role": m.role.name
                })

        # Build final list
        result = []
        for teacher in all_teachers:
            assignments = teacher_project_map.get(teacher.id)
            if assignments:
                for a in assignments:
                    result.append({
                        "teacher": teacher.username,
                        "project": a["project"],
                        "role": a["role"]
                    })
            else:
                result.append({
                    "teacher": teacher.username,
                    "project": "—",
                    "role": "—"
                })

        return Response(result)


    elif view_type == "proposals":
        if hasattr(user, "coordinator"):
            if user.coordinator.is_super:
                proposals = ProjectProposal.objects.all()
            elif user.coordinator.department:
                proposals = ProjectProposal.objects.filter(department=user.coordinator.department)
            else:
                proposals = ProjectProposal.objects.none()
        else:
            proposals = ProjectProposal.objects.filter(Q(submitted_by=user) | Q(proposed_to=user))
        return Response(ProjectProposalSerializer(proposals, many=True).data)

    elif view_type == "projects_by_coordinator":
        if not hasattr(user, "coordinator"):
            return Response({"detail": "Only coordinators can access this."}, status=403)
        if not user.coordinator.is_super:
            return Response({"detail": "Only super coordinators can view this report."}, status=403)

        all_coords = Coordinator.objects.select_related("department")
        result = []
        for coord in all_coords:
            dept = coord.department
            projects = Project.objects.filter(department=dept)
            result.append({
                "coordinator": coord.username,
                "department": dept.name if dept else None,
                "projects": ProjectSerializer(projects, many=True).data
            })
        return Response(result)

    return Response({"detail": "Invalid type parameter."}, status=400)