import json
from django.shortcuts import redirect, render, get_object_or_404
from django.db import transaction
from django.db.models import Prefetch, Q, OuterRef, Subquery, Exists, Count, F
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework import status
from .models import ProjectGoal, ProjectMembership, ProjectProposal, FeedbackExchange, Project, StudentProjectMembership, ProjectTask, ProjectLog
from .serializers import ProjectGoalSerializer, ProjectProposalSerializer, FeedbackExchangeSerializer, ProjectSerializer, ProjectTaskSerializer
from .services import calculate_completion_by_tasks, validate_student_limit, get_role_name_from_id, assign_project_memberships 
from users.serializers import StudentSerializer
from university.models import College, Department
from users.models import Role, Student, Supervisor, Coordinator
from users.services import is_teacher
from form.models import EvaluationForm


@login_required
def manage_proposals_view(request):
    user = request.user

    if hasattr(user, "coordinator"):
        if user.coordinator.is_super:
            proposals = ProjectProposal.objects.all().order_by("-created_at")
        elif user.coordinator.department:
            proposals = ProjectProposal.objects.filter(department=user.coordinator.department).order_by("-created_at")
        else:
            proposals = ProjectProposal.objects.none()

    else:
        proposals = ProjectProposal.objects.filter(submitted_by=user)

    feedbacks = FeedbackExchange.objects.filter(proposal__in=proposals)

    feedback_map = {}
    for fb in feedbacks:
        feedback_map[fb.proposal_id] = fb.feedback_text

    for p in proposals:
        p.teacher_feedback = feedback_map.get(p.id, None)

    context = {
        "proposals": proposals,
        "is_student": hasattr(user, "student"),
        "is_teacher": is_teacher(user),
        "is_coordinator": hasattr(user, "coordinator"),
    }

    if is_teacher(user) and user.department and user.department.college:
        college = user.department.college
        departments = Department.objects.filter(college=college)
        context["departments"] = departments

    return render(request, "project/add_proposals.html", context)

@login_required
def coordinator_proposals_view(request):
    user = request.user
    if not hasattr(user, "coordinator"):
        return redirect("home")

    if user.coordinator.is_super:
        proposals = ProjectProposal.objects.all().order_by("-created_at")
    elif user.coordinator.department:
        proposals = ProjectProposal.objects.filter(department=user.coordinator.department).order_by("-created_at")
    else:
        proposals = ProjectProposal.objects.none()

    return render(request, "project/coord_manage_proposals.html", {
        "proposals": proposals,
        
    })

@login_required
def teacher_proposals_view(request):
    if not is_teacher(request.user):
        return redirect("home")

    return render(request, "project/teacher_manage_proposals.html")

@login_required
def student_proposals_view(request):
    user = request.user

    if not is_teacher(user):
        return redirect("home")

    student_ids = Student.objects.values_list('id', flat=True)
    proposals = ProjectProposal.objects.filter(
        proposed_to=user,
        submitted_by_id__in=student_ids
    ).order_by('-created_at')

    context = {
        "student_proposals": proposals}

    return render(request, "project/student_proposals.html", context)


class ProjectProposalView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        user = request.user

        if pk:
            try:
                proposal = ProjectProposal.objects.get(pk=pk)

                is_owner = proposal.submitted_by == user
                is_recipient = proposal.proposed_to == user
                is_coordinator = hasattr(user, "coordinator")

                if is_coordinator:
                    if user.coordinator.is_super or (proposal.department == user.coordinator.department):
                        pass
                    elif not is_owner and not is_recipient:
                        return Response({'detail': 'Unauthorized access.'}, status=403)
                elif not is_owner and not is_recipient:
                    return Response({'detail': 'Unauthorized access.'}, status=403)

                serializer = ProjectProposalSerializer(proposal)
                response_data = serializer.data
                
                response_data["teacher_role"] = proposal.teacher_role.name if proposal.teacher_role else None
                response_data["teacher_role_id"] = proposal.teacher_role.id if proposal.teacher_role else None


                student_memberships = StudentProjectMembership.objects.filter(proposal=proposal).select_related('student')

                response_data["student_memberships"] = [
                    {
                        "id": sm.student.id,
                        "username": sm.student.username,
                        "first_name": sm.student.first_name,
                        "last_name": sm.student.last_name,
                    }
                    for sm in student_memberships
                    if sm.student
                ]


                response_data["duration"] = proposal.duration

                # Feedback
                feedback_qs = FeedbackExchange.objects.filter(
                    proposal=proposal
                    ).filter(
                        Q(receiver=proposal.submitted_by) | Q(receiver__isnull=True)
                    ).order_by("-created_at")
                feedback_obj = feedback_qs.first() if feedback_qs.exists() else None

                response_data["feedback_text"] = feedback_obj.feedback_text if feedback_obj else None
                response_data["feedback_sender_role"] = (
                    "Coordinator" if hasattr(feedback_obj.sender, "coordinator")
                    else "Teacher" if is_teacher(feedback_obj.sender)
                    else "Other"
                ) if feedback_obj else None

                return Response(response_data)

            except ProjectProposal.DoesNotExist:
                return Response({'detail': 'Proposal not found.'}, status=404)

        if hasattr(user, "coordinator"):
            if user.coordinator.is_super:
                proposals = ProjectProposal.objects.all().order_by("-created_at")
            elif user.coordinator.department:
                proposals = ProjectProposal.objects.filter(department=user.coordinator.department).order_by("-created_at")
            else:
                proposals = ProjectProposal.objects.none()
        else:
            proposals = ProjectProposal.objects.filter(
            Q(submitted_by=user) | Q(proposed_to=user)
            ).distinct()

        proposals_serializer = ProjectProposalSerializer(proposals, many=True)

        students_data = []
        teachers_data = []
        coordinators_data = []
        departments_data = []

        students = None

        if hasattr(user, 'student') and user.student.department and user.student.department.college:
            college = user.student.department.college
            students = Student.objects.filter(department__college=college).exclude(id=user.student.id)

            User = get_user_model()
            teacher_candidates = User.objects.filter(
                department__college=college
            ).exclude(
                id__in=Student.objects.values_list('id', flat=True)
            ).exclude(
                id__in=Coordinator.objects.values_list('id', flat=True)
            ).exclude(
                id__in=Supervisor.objects.values_list('id', flat=True)
            ).exclude(
                is_superuser=True
            )
            teachers_data = [
                {
                    "id": t.id,
                    "username": t.username,
                    "first_name": t.first_name,
                    "last_name": t.last_name
                }
                for t in teacher_candidates
            ]


        elif is_teacher(user) and user.department and user.department.college:
            college = user.department.college
            students = Student.objects.filter(department__college=college)
            students_data = StudentSerializer(students, many=True).data

            departments = Department.objects.filter(college=college)
            departments_data = [{'id': dept.id, 'name': dept.name} for dept in departments]

            coordinators = Coordinator.objects.filter(department__college=college)
            coordinators_data = [{'id': c.id, 'username': c.username} for c in coordinators]
    
        students_data = []
        if students:
            for s in students:
                students_data.append({
                    'id': s.id,
                    'username': s.username,
                    'first_name': s.first_name,
                    'last_name': s.last_name,
                    'student_id': s.student_id,
                    'already_assigned': StudentProjectMembership.objects.filter(
                            student=s,
                            project__isnull=False
                        ).exists() or StudentProjectMembership.objects.filter(
                            student=s,
                            proposal__isnull=False
                        ).exists()
                    })
    
        response_data["submitted_by"] = {
            "username": proposal.submitted_by.username,
            "first_name": proposal.submitted_by.first_name,
            "last_name": proposal.submitted_by.last_name,
        }

        return Response({
            'proposals': proposals_serializer.data,
            'students': students_data,
            'teachers': teachers_data,
            'coordinators': coordinators_data
        })

    def post(self, request):
        user = request.user

        if hasattr(user, 'coordinator'):
            return Response({'detail': 'Coordinators cannot submit proposals.'}, status=403)

        data = request.data.copy()

        if hasattr(user, 'student'):
            if StudentProjectMembership.objects.filter(student=user.student, project__isnull=False).exists():
                return Response({'detail': 'You are already assigned to a project and cannot submit a new proposal.'}, status=400)
    
            if user.student.department:
                data['department'] = user.student.department.id
            else:
                return Response({'detail': 'Student has no department.'}, status=400)
            data.pop("teacher_status", None)
            data.pop("coordinator_status", None)

        elif is_teacher(user):
            if 'department' in data:
                data['department'] = int(data['department'])
            else:
                return Response({'detail': 'Department is required for teachers.'}, status=400)
            data.pop("teacher_status", None)
            data.pop("coordinator_status", None)

        proposed_to_id = data.get('proposed_to')
        User = get_user_model()
        proposed_user = None
        if proposed_to_id:
            try:
                proposed_user = User.objects.get(id=proposed_to_id)
            except User.DoesNotExist:
                return Response({'detail': 'Proposed recipient not found.'}, status=400)

        duration = data.get('duration')
        if duration:
            try:
                data['duration'] = int(duration)
            except ValueError:
                return Response({'detail': 'Duration must be an integer.'}, status=400)

        team_members_ids = request.data.getlist("team_members_ids")
        try:
            validate_student_limit(request.data, is_proposal=True)
        except ValidationError as ve:
            return Response(ve.detail, status=400)

        serializer = ProjectProposalSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    proposal = serializer.save(submitted_by=user, proposed_to=proposed_user)

                    if is_teacher(user):
                        proposal.teacher_status = 'accepted'
                        proposal.save(update_fields=["teacher_status"])

                        if is_teacher(user):
                            teacher_status = data.get("teacher_status")
                            if teacher_status in dict(ProjectProposal.STATUS_CHOICES):
                                proposal.teacher_status = teacher_status

                            role_id = data.get("teacher_role_id")
                            if role_id:
                                try:
                                    role = Role.objects.get(id=role_id)
                                    proposal.teacher_role = role
                                    proposal.save(update_fields=["teacher_role"])
                                except Role.DoesNotExist:
                                    pass

                    if team_members_ids:
                        proposal.team_members.set(team_members_ids)

                    if hasattr(user, 'student'):
                        StudentProjectMembership.objects.create(student=user.student, proposal_id=proposal.id)

                    for sid in set(team_members_ids):
                        StudentProjectMembership.objects.get_or_create(
                        student_id=sid,
                        proposal=proposal
                    )
            except Exception as e:
                print("❌ Error creating proposal and memberships:", str(e))
                return Response({'detail': 'Failed to create proposal with team members.'}, status=400)

            return Response(ProjectProposalSerializer(proposal).data, status=201)

        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        user = request.user
        try:
            proposal = ProjectProposal.objects.get(pk=pk)
        except ProjectProposal.DoesNotExist:
            return Response({'detail': 'Proposal not found.'}, status=404)

        is_owner = proposal.submitted_by == user
        is_recipient = proposal.proposed_to == user
        is_coordinator = hasattr(user, "coordinator")

        if is_coordinator:
            if not user.coordinator.is_super:
                if proposal.department != user.coordinator.department:
                    return Response({'detail': 'Unauthorized.'}, status=403)
        elif not is_owner and not is_recipient:
            return Response({'detail': 'Unauthorized.'}, status=403)

        data = request.data

        # ✅ Safely convert duration
        duration = data.get('duration')
        if duration:
            try:
                proposal.duration = int(duration)
            except ValueError:
                return Response({'detail': 'Duration must be an integer.'}, status=400)

        # ✅ Update simple fields
        proposal.title = data.get("title", proposal.title)
        proposal.description = data.get("description", proposal.description)
        proposal.field = data.get("field", proposal.field)
        proposal.additional_comment = data.get("additional_comment", proposal.additional_comment)
        proposal.team_member_count = data.get("team_member_count", proposal.team_member_count)

        # ✅ Handle recipient (proposed_to)
        proposed_to_id = data.get("proposed_to")
        if proposed_to_id:
            User = get_user_model()
            try:
                proposed_user = User.objects.get(id=proposed_to_id)
                proposal.proposed_to = proposed_user
            except User.DoesNotExist:
                pass

        # ✅ Handle status updates
        if is_teacher(user):
            teacher_status = data.get("teacher_status")
            if teacher_status in dict(ProjectProposal.STATUS_CHOICES):
                proposal.teacher_status = teacher_status
            role_id = request.data.get("teacher_role_id")
            if role_id:
                try:
                    role = Role.objects.get(id=role_id)
                    proposal.teacher_role = role  # ✅ update it
                except Role.DoesNotExist:
                    pass
        elif hasattr(user, "coordinator"):
            coordinator_status = data.get("coordinator_status")
            if coordinator_status in dict(ProjectProposal.STATUS_CHOICES):
                proposal.coordinator_status = coordinator_status

        # ✅ Handle team members
        if "team_members_ids" in request.data:
            current_ids = set(
                StudentProjectMembership.objects.filter(proposal=proposal).values_list("student_id", flat=True)
            )
            new_ids = set(request.data.getlist("team_members_ids"))

            if hasattr(proposal.submitted_by, "student"):
                submitter_id = proposal.submitted_by.student.id
                new_ids.add(submitter_id)

            for sid in new_ids - current_ids:
                StudentProjectMembership.objects.create(student_id=sid, proposal=proposal)

            StudentProjectMembership.objects.filter(
                proposal=proposal,
                student_id__in=(current_ids - new_ids)
            ).exclude(student_id=submitter_id).delete()

        # ✅ Optional file upload support
        if 'attached_file' in request.FILES:
            proposal.attached_file = request.FILES['attached_file']

        # ✅ Enforce team size validation
        try:
            validate_student_limit(data, is_proposal=True)
        except ValidationError as ve:
            return Response(ve.detail, status=400)

        proposal.save()
        return Response(ProjectProposalSerializer(proposal).data)

    def delete(self, request, pk):
        user = request.user
        try:
            proposal = ProjectProposal.objects.get(pk=pk)
            if proposal.submitted_by != user:
                return Response({'detail': 'Not allowed to delete this.'}, status=403)
        except ProjectProposal.DoesNotExist:
            return Response({'detail': 'Proposal not found.'}, status=404)

        StudentProjectMembership.objects.filter(proposal=proposal).delete()

        Project.objects.filter(proposal=proposal).delete()

        proposal.delete()

        return Response({'detail': 'Proposal deleted successfully.'}, status=204)


class FeedbackExchangeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        report_id = request.GET.get("report_id")
        proposal_id = request.GET.get("proposal")
        project_id = request.GET.get("project")
        task_id = request.GET.get("task")
        

        # Allow filtering by exactly one target
        if report_id:
            feedbacks = FeedbackExchange.objects.filter(report_id=report_id).order_by("-created_at")
        elif proposal_id:
            feedbacks = FeedbackExchange.objects.filter(proposal_id=proposal_id).order_by("-created_at")
        elif project_id:
            feedbacks = FeedbackExchange.objects.filter(project_id=project_id).order_by("-created_at")
        elif task_id:
            feedbacks = FeedbackExchange.objects.filter(task_id=task_id).order_by("-created_at")
        else:
            # Default fallback (e.g. personal feedbacks)
            if hasattr(user, "student"):
                feedbacks = FeedbackExchange.objects.filter(
                    Q(receiver=user) | Q(receiver__isnull=True),
                    proposal__submitted_by=user,
                    proposal__isnull=False
                ).order_by("-created_at")
            else:
                feedbacks = FeedbackExchange.objects.filter(sender=user).order_by("-created_at")

        data = []
        for fb in feedbacks:
            entry = {
                "id": fb.id,
                "sender_name": fb.sender.get_full_name() or fb.sender.username,
                "message": fb.feedback_text,
                "created_at": fb.created_at,
            }

            if fb.comment:
                entry["comment"] = fb.comment

            if fb.feedback_file:
                entry["feedback_file"] = fb.feedback_file.url

            if hasattr(fb, "reply"):
                entry["reply"] = {
                    "message": fb.reply.feedback_text,
                    "created_at": fb.reply.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }

            data.append(entry)

        return Response(data)

    def post(self, request):
        user = request.user
        data = request.data.copy()
        data["sender"] = user.id
        print("Received data:", data)

        proposal_id = data.get("proposal")
        project_id = data.get("project")
        task_id = data.get("task_id")
        report_id = data.get("report")
        print("Received data2:", data)

        non_empty = [key for key in [proposal_id, project_id, task_id, report_id] if key]
        if len(non_empty) != 1:
            return Response({"detail": "Exactly one of proposal, project, task, or report must be provided."}, status=400)

        if task_id:
            try:
                task = ProjectTask.objects.get(id=task_id)
                if project_id and str(task.project.id) != str(project_id):
                    return Response({"detail": "Task does not belong to the specified project."}, status=400)
                data["task"] = task.id
            except ProjectTask.DoesNotExist:
                return Response({"detail": "Task not found."}, status=400)

        if report_id:
            data["report"] = report_id

        serializer = FeedbackExchangeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


@login_required
def manage_project_landing_view(request):
    return render(request, "project/coord_manage_projects.html")

@login_required
def manage_projects_view(request):
    user = request.user
    if not hasattr(user, "coordinator"):
        return redirect("home")

    coordinator = Coordinator.objects.get(id=user.coordinator.id)

    if coordinator.is_super:
        # ✅ Show only projects where department belongs to coordinator's college
        if coordinator.department and coordinator.department.college:
            projects = Project.objects.filter(
                department__college=coordinator.department.college
            ).select_related("proposal", "proposal__submitted_by", "department").order_by("-id")
            departments = Department.objects.filter(college=coordinator.department.college)
        else:
            projects = Project.objects.none()
            departments = Department.objects.none()
    else:

        projects = Project.objects.filter(
            department=coordinator.department
        ).select_related("proposal", "proposal__submitted_by", "department").order_by("-id")
        departments = None

    
    for project in projects:
        supervisor_membership = ProjectMembership.objects.filter(
            project=project, role__name="Supervisor"
        ).select_related("user").first()

        reader_membership = ProjectMembership.objects.filter(
            project=project, role__name="Reader"
        ).select_related("user").first()

        judge_memberships = ProjectMembership.objects.filter(
            project=project, role__name="Judgement Committee"
        ).select_related("user")

        project.supervisor_user = supervisor_membership.user if supervisor_membership else None
        project.supervisor_name = (
            f"{supervisor_membership.user.first_name} {supervisor_membership.user.last_name}".strip()
            if supervisor_membership and supervisor_membership.user else None
        )

        project.reader_user = reader_membership.user if reader_membership else None
        project.reader_name = (
            f"{reader_membership.user.first_name} {reader_membership.user.last_name}".strip()
            if reader_membership and reader_membership.user else None
        )

        project.judges_names = [
            f"{m.user.first_name} {m.user.last_name}".strip() if m.user else ""
            for m in judge_memberships
        ] if judge_memberships.exists() else []

        print("📦 Project:", project.name)
        print("🧑‍🏫 Supervisor Name:", project.supervisor_name)
        print("📘 Reader Name:", project.reader_name)
        print("👩‍⚖️ Judges:", project.judges_names)

    return render(request, "project/manage_projects.html", {
        "projects": projects,
        "is_super_coord": coordinator.is_super,
        "departments": departments,
        "coord_dept_id": coordinator.department.id if not coordinator.is_super else None
    })


class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        print("🔍 Project GET request received")

        if request.query_params.get("users_only") == "true":
            return self.get_user_options()

        if pk:
            print(f"🔍 Fetching single project with id={pk}")
            try:
                project = Project.objects.get(pk=pk)
                serializer = ProjectSerializer(project)
                return Response(serializer.data)
            except Project.DoesNotExist:
                return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.query_params.get("available") == "true":
            print("📥 Fetching available projects for students...")

            # Get projects with no students or partially filled teams
            projects = Project.objects.annotate(
                assigned_count=Count("studentprojectmembership")
            ).filter(
                Q(assigned_count__lt=F("team_member_count")) | Q(team_member_count=0)
            )

            serializer = ProjectSerializer(projects.order_by("-id"), many=True)
            return Response(serializer.data)

        # Normal list view with optional search
        search = request.query_params.get('search', '').strip()
        print(f"📎 Search term: '{search}'")

        projects = Project.objects.all().order_by("-id")

        if search:
            projects = projects.filter(
                Q(name__icontains=search) |
                Q(student_memberships__student__username__icontains=search) |
                Q(student_memberships__student__student_id__icontains=search) |
                Q(supervisor__username__icontains=search)
            ).distinct()

        print(f"📦 Total projects returned: {projects.count()}")
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def get_user_options(self):
        User = get_user_model()
        students = Student.objects.all()
        assigned_ids = set(
            StudentProjectMembership.objects.values_list("student_id", flat=True)
        )

        student_list = [
        {
            "id": s.id,
            "username": s.username,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "is_assigned": s.id in assigned_ids
        }
        for s in students
    ]


        all_users = User.objects.exclude(is_superuser=True)
        teacher_list = [
        {
            "id": u.id,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name
        }
        for u in all_users if is_teacher(u)
    ]


        return Response({
            "students": student_list,
            "teachers": teacher_list
        })


    def post(self, request):
        mutable_data = request.data.copy()

        if hasattr(request.user, "coordinator") and not request.user.coordinator.is_super:
            mutable_data["coordinator"] = request.user.coordinator.id

        duration = mutable_data.get("duration")
        if duration:
            try:
                mutable_data["duration"] = int(duration)
            except ValueError:
                return Response({'detail': 'Duration must be an integer.'}, status=400)

        try:
            validate_student_limit(mutable_data, is_proposal=True)
        except ValidationError as ve:
            return Response(ve.detail, status=400)

    # Extract and pop extra fields
        student_ids = mutable_data.pop('student_ids', [])
        memberships = mutable_data.pop('memberships', [])

        serializer = ProjectSerializer(data=mutable_data)

        if serializer.is_valid():
            project = serializer.save()

            for sid in student_ids:
                StudentProjectMembership.objects.create(student_id=sid, project=project)

            print("📦 memberships payload:", memberships)

            if hasattr(request.user, "coordinator"):
                coordinator_role = Role.objects.filter(name__iexact="Coordinator").first()
                if coordinator_role:
                    ProjectMembership.objects.get_or_create(
                            user=request.user,
                            project=project,
                            role=coordinator_role
                    )
            assign_project_memberships(project, memberships)

            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        duration = request.data.get("duration")
        if duration:
            try:
                request.data["duration"] = int(duration)
            except ValueError:
                return Response({'detail': 'Duration must be an integer.'}, status=400)

        # validate team member count
        try:
            validate_student_limit(request.data, is_proposal=True)
        except ValidationError as ve:
            return Response(ve.detail, status=400)

        # Extract student and memberships for update
        student_ids = request.data.get("student_ids", [])
        memberships = request.data.get("memberships", [])

        serializer = ProjectSerializer(project, data=request.data, partial=True)

        if serializer.is_valid():
            updated_project = serializer.save()

            if 'research_file' in request.FILES:
                updated_project.research_file = request.FILES['research_file']
                updated_project.save(update_fields=['research_file'])

            if "student_ids" in request.data:
                current_ids = set(StudentProjectMembership.objects.filter(project=updated_project).values_list("student_id", flat=True))
                new_ids = set(student_ids)

                # Add new students
                for sid in new_ids - current_ids:
                    StudentProjectMembership.objects.create(student_id=sid, project=updated_project)

                # Remove students not in the new list
                StudentProjectMembership.objects.filter(project=updated_project, student_id__in=(current_ids - new_ids)).delete()

            ProjectMembership.objects.filter(project=updated_project).delete()
            print("📦 memberships payload:", memberships)
    
            assign_project_memberships(updated_project, memberships)
            return Response(ProjectSerializer(updated_project).data)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        project.delete()
        return Response({"detail": "Project deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@login_required
def track_projects_landing_view(request):
    is_super = hasattr(request.user, "coordinator") and request.user.coordinator.is_super
    return render(request, "project/track_project.html", {
        "is_super_coord": is_super
    }
)

@login_required
def track_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_super = hasattr(request.user, "coordinator") and request.user.coordinator.is_super

    return render(request, "project/track_project.html", {
        "project_id": project.id,
        "project_name": project.name,
        "is_super_coord": is_super
    })

@login_required
def teacher_projects_page(request):
    user = request.user

    if not is_teacher(user):
        return redirect("home")

    print("🔍 Logged in teacher:", user.username, "| ID:", user.id)

    memberships = ProjectMembership.objects.select_related(
        "project", "role", "project__department"
    ).filter(user_id=user.id)

    print(f"🔎 Total memberships found: {memberships.count()}")

    projects = []
    for membership in memberships:
        if membership.project:
            project = membership.project
            project.my_role = membership.role.name if membership.role else "Unassigned"
            print("➡️ Project found:", project.name, "| Role:", project.my_role)
            projects.append(project)

    if not projects:
        print("⚠️ No projects found despite existing membership. Possible issue with role or project link.")

    print(f"📦 Total projects to render: {len(projects)}")

    return render(request, "project/teacher_projects.html", {
        "projects": projects
    })

def student_project_page(request):
    return render(request, "project/student_project.html")

@login_required
def project_tasks_page(request):
    return render(request, 'project/project_tasks.html')


class TrackProjectView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk=None):
        print("🔍 Project GET request received")

        if pk:
            print(f"🔎 Fetching details for project ID {pk}")
            try:
                project = Project.objects.select_related(
                    "plan", "supervisor", "coordinator", "department"
                ).get(pk=pk)
                print(f"✅ Found project: {project.name}")
            except Project.DoesNotExist:
                return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

            from .serializers import MembershipReadSerializer  # make sure it's imported

            project_data = ProjectSerializer(project).data
            project_data["members"] = MembershipReadSerializer(
                ProjectMembership.objects.filter(project=project).select_related("user", "role"), 
                many=True
            ).data

            students = StudentProjectMembership.objects.filter(project=project).select_related('student')
            tasks = ProjectTask.objects.filter(project=project)
            goals = ProjectGoal.objects.filter(project=project)

            # ✅ Group tasks under each goal with assign_to_name
            goals_data = []
            for goal in goals:
                goal_tasks = tasks.filter(goal=goal)
                task_serialized = ProjectTaskSerializer(goal_tasks, many=True).data

                for t in task_serialized:
                    task_obj = goal_tasks.get(id=t["id"])
                    if task_obj.assign_to:
                        t["assign_to"] = task_obj.assign_to.id  # <-- This is the key fix
                        t["assign_to_name"] = task_obj.assign_to.username
                    else:
                        t["assign_to"] = None
                        t["assign_to_name"] = None

                goals_data.append({
                    "id": goal.id,
                    "goal": goal.goal,
                    "duration": goal.duration,
                    "created_at": goal.created_at,
                    "tasks": task_serialized
                })

            tasks_data = ProjectTaskSerializer(tasks, many=True).data
            completion = round(calculate_completion_by_tasks(project), 2)
            print(f"🧮 Completion Status for project {project.id}: {completion}")

            # ✅ Include feedbacks from all teaching roles
            feedbacks = FeedbackExchange.objects.filter(project=project).order_by("-created_at")
            print("🔁 Total Feedbacks Found:", feedbacks.count())
            for fb in feedbacks:
                print("📝 Feedback:", {
                    "sender": f"{fb.sender.first_name} {fb.sender.last_name}".strip(),
                    "sender_role": (
                        "Coordinator" if hasattr(fb.sender, "coordinator")
                        else "Teacher" if is_teacher(fb.sender)
                        else "Reader" if fb.sender.projectmembership_set.filter(project=project, role__name="Reader").exists()
                        else "Judgement Committee" if fb.sender.projectmembership_set.filter(project=project, role__name="Judgement Committee").exists()
                        else "Other"
                    ),
                    "text": fb.feedback_text,
                    "file": fb.feedback_file.url if fb.feedback_file else None,
                    "created": fb.created_at
                })
    
            visible_feedbacks = [
                {
                    "sender": f"{fb.sender.first_name} {fb.sender.last_name}".strip(),

                    "sender_role": (
                        "Reader" if fb.sender.projectmembership_set.filter(project=project, role__name="Reader").exists()
                        else "Judgement Committee" if fb.sender.projectmembership_set.filter(project=project, role__name="Judgement Committee").exists()
                        else "Other"
                    ),
                    "feedback_text": fb.feedback_text,
                    "created_at": fb.created_at.strftime("%Y-%m-%d %H:%M"),
                    "feedback_file": fb.feedback_file.url if fb.feedback_file else None
                }
                for fb in feedbacks
                if fb.sender.projectmembership_set.filter(project=project, role__name__in=["Reader", "Judgement Committee"]).exists()
            ]

            return Response({
                "project": project_data,
                "supervisor_name": project.supervisor.get_full_name() if project.supervisor else None,
                "students": [
                    {
                        "id": s.student.id,
                        "username": s.student.username,
                        "first_name": s.student.first_name,
                        "last_name": s.student.last_name,
                        "email": s.student.email,
                        "phone": getattr(s.student, "phone_number", "N/A"),
                    }
                    for s in students
                ],

                "completion_status": completion,
                "goals": goals_data,
                "tasks": tasks_data,
                "research_file": project.research_file.url if project.research_file else None,
                "logs": [],
                "feedbacks": visible_feedbacks,
            })
        else:
            print("📜 Listing projects (coordinator or student view)")
            user = request.user
            projects = Project.objects.none()
            departments_data = []

            if hasattr(user, "coordinator"):
                if user.coordinator.is_super:
                    if user.coordinator.department and user.coordinator.department.college:
                        projects = Project.objects.filter(department__college=user.coordinator.department.college)
                        departments_data = [{"id": d.id, "name": d.name} for d in Department.objects.filter(college=user.coordinator.department.college)]
                else:
                    if user.coordinator.department:
                        projects = Project.objects.filter(department=user.coordinator.department)
            else:
                student_membership = StudentProjectMembership.objects.filter(student=user).select_related('project').first()
                if student_membership and student_membership.project:
                    projects = Project.objects.filter(id=student_membership.project.id)

            projects_data = ProjectSerializer(projects, many=True).data
            students = StudentProjectMembership.objects.filter(project__in=projects).select_related('student')

            return Response({
                "projects": projects_data,
                "departments": departments_data,
                "students": [
                    {
                        "id": s.student.id,
                        "username": s.student.username,
                        "first_name": s.student.first_name,
                        "last_name": s.student.last_name,
                        "email": s.student.email,
                        "phone": getattr(s.student, "phone_number", "N/A"),
                    }
                    for s in students
                ],

            })

    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        user = request.user

        if 'comment' in request.data or 'report_file' in request.FILES:
            FeedbackExchange.objects.create(
                project=project,
                sender=user,
                feedback_text=request.data.get('comment', ''),
                feedback_file=request.FILES.get('report_file')
            )
            return Response({"detail": "Feedback submitted successfully."}, status=201)


        elif 'task_name' in request.data and 'goal_id' in request.data:
            print("📥 Incoming data for task:", request.data)
            task_name = request.data.get('task_name')
            task_goal_text = request.data.get('goal_text', '')  # ✅ correct name
            goal_id = request.data.get('goal_id')
            outputs = request.data.get('outputs', '')
            assign_to_id = request.data.get('assign_to')
            deadline_days = request.data.get('deadline_days')
            task_status = request.data.get('task_status', 'to do')

            if not task_name or not assign_to_id:
                return Response({"detail": "Missing required fields to create task."}, status=400)

            ProjectTask.objects.create(
                project=project,
                goal_id=goal_id,
                name=task_name,
                goals=task_goal_text,  # editable text field (label)
                outputs=outputs,
                assign_to_id=assign_to_id,
                deadline_days=deadline_days,
                task_status=task_status,
            )
            return Response({"detail": "Task created successfully."}, status=201)

        elif 'task_id' in request.data and ('deliverable_text' in request.data or 'deliverable_file' in request.FILES):
            task_id = request.data.get('task_id')
            try:
                task = ProjectTask.objects.get(id=task_id, project=project)
                task.deliverable_text = request.data.get('deliverable_text', task.deliverable_text)
                if 'deliverable_file' in request.FILES:
                    task.deliverable_file = request.FILES['deliverable_file']
                if 'task_status' in request.data:
                    task.task_status = request.data.get('task_status')
                task.save()
                return Response({"detail": "Task progress updated successfully."})
            except ProjectTask.DoesNotExist:
                return Response({"detail": "Task not found."}, status=404)

        elif 'feedback_text' in request.data:
            FeedbackExchange.objects.create(
                project=project,
                sender=user,
                task_id=request.data.get('task_id'),
                feedback_text=request.data.get('feedback_text'),
                feedback_file=request.FILES.get('feedback_file')
            )
            return Response({"detail": "Feedback submitted successfully."}, status=201)

        elif 'goal_text' in request.data and 'duration' in request.data:
            goal_text = request.data.get('goal_text')
            duration = request.data.get('duration')

            if not goal_text:
                return Response({"detail": "Goal text is required."}, status=400)

            ProjectGoal.objects.create(
                project=project,
                goal=goal_text,
                duration=duration
            )
            return Response({"detail": "Goal created successfully."}, status=201)

        return Response({"detail": "Invalid request. Missing required fields."}, status=400)

    def put(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        user = request.user

        # ✅ Check if task update is intended
        task_id = request.data.get('task_id')
        if task_id:
            try:
                task = ProjectTask.objects.get(id=task_id, project=project)

                # ✅ Update basic editable fields only if present
                if 'name' in request.data:
                    task.name = request.data['name']

                if 'task_status' in request.data:
                    task.task_status = request.data['task_status']

                if 'deliverable_text' in request.data:
                    task.deliverable_text = request.data['deliverable_text']

                if 'outputs' in request.data:
                    task.outputs = request.data['outputs']

                if 'deadline_days' in request.data:
                    task.deadline_days = request.data['deadline_days']

                if 'task_goal_text' in request.data:
                    task.goals = request.data['task_goal_text']

                # ✅ Update foreign keys if provided
                if 'goal_id' in request.data:
                    task.goal_id = request.data['goal_id']

                if 'assign_to' in request.data:
                    task.assign_to_id = request.data['assign_to']

                # ✅ Handle file upload safely
                if 'deliverable_file' in request.FILES:
                    task.deliverable_file = request.FILES['deliverable_file']

                task.save()
                return Response({"detail": "Task updated successfully."})

            except ProjectTask.DoesNotExist:
                return Response({"detail": "Task not found."}, status=404)

        return Response({"detail": "Invalid PUT request. Missing fields."}, status=400)

    def delete(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        goal_id = request.data.get('goal_id')
        if not goal_id:
            return Response({"detail": "Goal ID is required to delete goal."}, status=400)

        try:
            goal = ProjectGoal.objects.get(id=goal_id, project=project)
            goal.delete()
            return Response({"detail": "Goal deleted successfully."})
        except ProjectGoal.DoesNotExist:
            return Response({"detail": "Goal not found."}, status=404)

@login_required
def available_projects_view(request):
    user = request.user

    available_projects = (
        Project.objects
        .prefetch_related("memberships__user", "memberships__role", "student_memberships")
        .annotate(assigned_count=Count("student_memberships"))
        .order_by("-id")
    )

    projects_data = []
    for project in available_projects:
        assigned_count = project.student_memberships.count()
        is_full = (project.team_member_count > 0 and assigned_count >= project.team_member_count)

        assigned_students = [
            f"{m.student.first_name} {m.student.last_name}".strip()
            if m.student.first_name or m.student.last_name
            else m.student.username
            for m in project.student_memberships.all()
        ]
        supervisor = next((m.user for m in project.memberships.all() if m.role.name == "Supervisor"), None)
        reader = next((m.user for m in project.memberships.all() if m.role.name == "Reader"), None)
        judges = [m.user for m in project.memberships.all() if m.role.name == "Judgement Committee"]

        projects_data.append({
            "project": project,
            "assigned_students": assigned_students,
            "supervisor": supervisor,
            "reader": reader,
            "judges": [f"{j.first_name} {j.last_name}".strip() for j in judges],
            "is_full": is_full,
        })

    context = {
        "available_projects": projects_data
    }

    if hasattr(user, "student"):
        context["student"] = user
        context["joined_project_ids"] = list(
            StudentProjectMembership.objects
            .filter(student=user.student)
            .values_list("project_id", flat=True)
        )
    elif is_teacher(user):
        teacher_roles = {
            m.project_id: m.role.name
            for m in ProjectMembership.objects.filter(user=user)
        }
        context["teacher_roles"] = teacher_roles
        context["joined_teacher_project_ids"] = list(teacher_roles.keys())
    else:
        return redirect("home")

    return render(request, "project/available_projects.html", context)


@login_required
def teacher_view_project(request, project_id):
    user = request.user
    if not is_teacher(user):
        return redirect("home")

    project = get_object_or_404(
        Project.objects.prefetch_related(
            "student_memberships__student",
            Prefetch("memberships", queryset=ProjectMembership.objects.select_related("user", "role")),
        ),
        pk=project_id
    )

    # Determine teacher's role in this project
    my_membership = project.memberships.filter(user=user).first()
    my_role = my_membership.role.name if my_membership else "N/A"

    student_members = [m.student for m in project.student_memberships.all()]
    teacher_members = [{
        "name": f"{m.user.first_name} {m.user.last_name}".strip() or m.user.username,
        "role": m.role.name,
        "email": m.user.email,
        "phone_number": getattr(m.user, "phone_number", "N/A")
    } for m in project.memberships.exclude(user=user)]

    form_available = EvaluationForm.objects.filter(target_role=my_membership.role).exists() if my_membership else False

    context = {
        "project": project,
        "my_role": my_role,
        "student_members": student_members,
        "teacher_members": teacher_members,
        "assessment_submitted": form_available,
    }
    return render(request, "project/teacher_view_project.html", context)

@login_required
def project_progress_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = ProjectTask.objects.filter(project=project).select_related("assign_to")

    return render(request, 'project/progress_view.html', {
        "project": project,
        "project_tasks": tasks
    })

class AvailableProjectActionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Project.objects.annotate(
            assigned_count=Count("student_memberships")
        ).filter(
            Q(assigned_count__lt=F("team_member_count")) | Q(team_member_count=0)
        ).order_by("-id")

        from .serializers import ProjectSerializer
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, project_id=None):
        user = request.user
        role_name = request.data.get("role")

        if not project_id:
            return Response({"detail": "Missing project_id."}, status=400)

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        # ✅ Student joins
        if hasattr(user, "student"):
            # ❌ Already in *any* project
            if StudentProjectMembership.objects.filter(student=user.student).exists():
                return Response({"detail": "You are already assigned to another project."}, status=400)

            # ❌ Already in this project
            if StudentProjectMembership.objects.filter(student=user.student, project=project).exists():
                return Response({"detail": "Already joined this project."}, status=400)

            # ❌ Project full
            current_count = StudentProjectMembership.objects.filter(project=project).count()
            if current_count >= project.team_member_count > 0:
                return Response({"detail": "Project team is full."}, status=400)

            # ✅ Join
            StudentProjectMembership.objects.create(student=user.student, project=project)
            return Response({"detail": "Successfully joined the project."})

        # ✅ Teacher joins with a role
        elif is_teacher(user):
            if not role_name:
                return Response({"detail": "Missing role for teacher."}, status=400)

            try:
                role = Role.objects.get(name__iexact=role_name)
            except Role.DoesNotExist:
                return Response({"detail": f"Invalid role: {role_name}"}, status=400)

            if ProjectMembership.objects.filter(user=user, project=project).exists():
                return Response({"detail": "You already have a role in this project."}, status=400)

            ProjectMembership.objects.create(user=user, project=project, role=role)
            return Response({"detail": f"Added as {role.name}."})

        return Response({"detail": "Only students or teachers can join projects."}, status=403)

    def delete(self, request, project_id =None):
        user = request.user
        if not project_id:
            return Response({"detail": "Missing project_id."}, status=400)

        # ✅ Student leaves
        if hasattr(user, "student"):
            deleted, _ = StudentProjectMembership.objects.filter(
                student=user, project_id=project_id
            ).delete()

            if deleted:
                return Response({"detail": "Successfully left the project."})
            return Response({"detail": "You are not part of this project."}, status=400)

        # ✅ Teacher removes role
        elif is_teacher(user):
            deleted, _ = ProjectMembership.objects.filter(
                user=user, project_id=project_id
            ).delete()

            if deleted:
                return Response({"detail": "Your role has been removed."})
            return Response({"detail": "You are not assigned to this project."}, status=400)

        return Response({"detail": "Only students or teachers can leave projects."}, status=403)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_task_detail(request, task_id):
    print(f"🔍 get_task_detail called with task_id: {task_id}") 
    try:
        task = ProjectTask.objects.select_related('goal', 'assign_to', 'project').get(pk=task_id)
        print(f"✅ Task found: {task.name} (ID: {task.id})")

        task_data = {
            "id": task.id,
            "name": task.name,
            "task_status": task.task_status,
            "goals": task.goals,
            "goal": {
                "id": task.goal.id,
                "goal": task.goal.goal
            } if task.goal else None,
            "outputs": task.outputs,
            "assign_to": task.assign_to.id if task.assign_to else None,
            "assign_to_name": task.assign_to.username if task.assign_to else None,
            "deadline_days": task.deadline_days,
            "deliverable_text": task.deliverable_text,
            "deliverable_file": task.deliverable_file.url if task.deliverable_file else None,
            "created_at": task.created_at.strftime("%Y-%m-%d"),
            "updated_at": task.updated_at.strftime("%Y-%m-%d"),
            "project": task.project.id,
        }

        # Now attach feedbacks
        task_data["feedbacks"] = [
            {
                "sender": f"{fb.sender.first_name} {fb.sender.last_name}".strip(),
                "sender_role": (
                    "Coordinator" if hasattr(fb.sender, "coordinator")
                    else "Teacher" if is_teacher(fb.sender)
                    else "Student" if hasattr(fb.sender, "student")
                    else "Unknown"
                ),
                "feedback_text": fb.feedback_text,
                "created_at": fb.created_at.strftime("%Y-%m-%d %H:%M"),
                "feedback_file": fb.feedback_file.url if fb.feedback_file else None
            }
            for fb in FeedbackExchange.objects.filter(task=task).order_by("-created_at")
        ]

        print("📦 Returning task data:", task_data)
        return Response(task_data)

    except ProjectTask.DoesNotExist:
        return Response({"detail": "Task not found."}, status=404)


from django.http import JsonResponse

def coordinator_dashboard_stats(request):
    user = request.user

    try:
        coordinator = user.coordinator  # assuming OneToOneField from User to Coordinator
    except Coordinator.DoesNotExist:
        return JsonResponse({"error": "Not a coordinator"}, status=403)

    if coordinator.is_super:
        projects = Project.objects.all()
        proposals = ProjectProposal.objects.filter(coordinator_status='pending')
    else:
        projects = Project.objects.filter(department=coordinator.department)
        proposals = ProjectProposal.objects.filter(coordinator_status='pending', department=coordinator.department)

    total = projects.count()
    ongoing = projects.filter(plan__completion_status__lt=100).count()
    completed = projects.filter(plan__completion_status=100).count()

    active_fields = (projects
        .values('field')
        .annotate(count=Count('id'))
        .order_by('-count'))

    return JsonResponse({
        "total_projects": total,
        "ongoing_projects": ongoing,
        "completed_projects": completed,
        "pending_proposals": proposals.count(),
        "most_active_fields": list(active_fields),
    })


@login_required
def coordinator_dashboard_page(request):
    return render(request, "coordinator/dashboard.html")


from datetime import timedelta, date

def student_dashboard_stats(request):
    user = request.user

    if not hasattr(user, "student"):
        return JsonResponse({"error": "Not a student"}, status=403)

    tasks = ProjectTask.objects.filter(assign_to=user)
    summary = {
        "to do": tasks.filter(task_status="to do").count(),
        "in progress": tasks.filter(task_status="in progress").count(),
        "done": tasks.filter(task_status="done").count(),
    }

    today = date.today()
    deadline_range = today + timedelta(days=7)
    upcoming_tasks = tasks.filter(deadline_days__isnull=False).order_by("deadline_days")

    upcoming = [
        {
            "name": t.name,
            "deadline": (t.created_at.date() + timedelta(days=t.deadline_days)).isoformat(),
            "status": t.task_status,
        }
        for t in upcoming_tasks
        if t.created_at and today <= t.created_at.date() + timedelta(days=t.deadline_days) <= deadline_range
    ]

    return JsonResponse({
        "task_summary": summary,
        "upcoming_deadlines": upcoming
    })

@login_required
def student_dashboard_page(request):
    return render(request, "student/dashboard.html")
