from django.shortcuts import redirect, render, get_object_or_404
from django.db import transaction
from django.db.models import Q, OuterRef, Subquery, Exists
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework import status
from .models import ProjectMembership, ProjectProposal, FeedbackExchange, Project, StudentProjectMembership, ProjectTask, ProjectLog
from .serializers import ProjectProposalSerializer, FeedbackExchangeSerializer, ProjectSerializer
from .services import validate_student_limit, get_role_name_from_id, assign_project_memberships 
from users.serializers import StudentSerializer
from university.models import College, Department
from users.models import Role, Student, Supervisor, Coordinator
from users.services import is_teacher


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

                student_memberships = StudentProjectMembership.objects.filter(proposal=proposal).select_related('student')

                response_data["student_memberships"] = [
                    {
                        "id": sm.student.id,
                        "username": sm.student.username
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
            teachers_data = [{'id': t.id, 'username': t.username} for t in teacher_candidates]

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
                    'student_id': s.student_id,
                    'already_assigned': StudentProjectMembership.objects.filter(
                            student=s,
                            project__isnull=False
                        ).exists() or StudentProjectMembership.objects.filter(
                            student=s,
                            proposal__isnull=False
                        ).exists()
                    })
    
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

                    if team_members_ids:
                        proposal.team_members.set(team_members_ids)

                    if hasattr(user, 'student'):
                        StudentProjectMembership.objects.create(student=user.student, proposal_id=proposal.id)

                    for sid in team_members_ids:
                        if not StudentProjectMembership.objects.filter(student_id=sid, proposal_id=proposal.id).exists():
                            StudentProjectMembership.objects.create(student_id=sid, proposal_id=proposal.id)

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

        data = request.data.copy()

        duration = data.get('duration')
        if duration:
            try:
                data['duration'] = int(duration)
            except ValueError:
                return Response({'detail': 'Duration must be an integer.'}, status=400)

        proposed_to_id = data.get('proposed_to')

        User = get_user_model()
        proposed_user = None
        if proposed_to_id:
            try:
                proposed_user = User.objects.get(id=proposed_to_id)
            except User.DoesNotExist:
                pass

        data['submitted_by'] = proposal.submitted_by.id
        data['department'] = proposal.department.id if proposal.department else None

        update_fields = {}

        if is_teacher(user):
            teacher_status = data.get("teacher_status")
            if teacher_status in dict(ProjectProposal.STATUS_CHOICES):
                update_fields["teacher_status"] = teacher_status
        elif hasattr(user, "coordinator"):
            coordinator_status = data.get("coordinator_status")
            if coordinator_status in dict(ProjectProposal.STATUS_CHOICES):
                update_fields["coordinator_status"] = coordinator_status
        elif hasattr(user, "student"):
            data.pop("teacher_status", None)
            data.pop("coordinator_status", None)

        team_members_ids = request.data.getlist("team_members_ids")
        if team_members_ids:
            proposal.team_members.set(team_members_ids)

        StudentProjectMembership.objects.filter(proposal=proposal).delete()

        if hasattr(proposal.submitted_by, "student"):
            StudentProjectMembership.objects.create(student=proposal.submitted_by.student, proposal=proposal)

        for sid in team_members_ids:
            if not StudentProjectMembership.objects.filter(student_id=sid, proposal=proposal).exists():
                StudentProjectMembership.objects.create(student_id=sid, proposal=proposal)

        for field, value in update_fields.items():
            setattr(proposal, field, value)

        if proposed_user:
            proposal.proposed_to = proposed_user

        try:
            validate_student_limit(request.data, is_proposal=True)
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

        proposal.delete()
        return Response({'detail': 'Proposal deleted successfully.'}, status=204)


class FeedbackExchangeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if hasattr(user, "student"):
            feedbacks = FeedbackExchange.objects.filter(
                Q(receiver=user) | Q(receiver__isnull=True),
                proposal__submitted_by=user,
                proposal__isnull=False
            ).order_by("-created_at")
        else:
            feedbacks = FeedbackExchange.objects.filter(sender=user).order_by("-created_at")

        serializer = FeedbackExchangeSerializer(feedbacks, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user

        if not (is_teacher(user) or hasattr(user, "coordinator")):
            return Response({"detail": "Only teachers and coordinators can send feedback."}, status=403)

        data = request.data.copy()
        data["sender"] = user.id

        proposal_id = data.get("proposal")
        project_id = data.get("project")

        if not proposal_id and not project_id:
            return Response({"detail": "Either proposal or project must be specified."}, status=400)

        if proposal_id and project_id:
            return Response({"detail": "Only one of proposal or project should be specified."}, status=400)

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
            project=project,
            role__name="Supervisor"
        ).select_related("user").first()
        project.supervisor_user = supervisor_membership.user if supervisor_membership else None

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

        search = request.query_params.get('search', '').strip()
        print(f"📎 Search term: '{search}'")

        projects = Project.objects.all().order_by("-id")

        if search:
            projects = projects.filter(
                Q(name__icontains=search) |  # ← added this
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
            {"id": s.id, "username": s.username, "is_assigned": s.id in assigned_ids}
            for s in students
        ]

        all_users = User.objects.exclude(is_superuser=True)
        teacher_list = [{"id": u.id, "username": u.username} for u in all_users if is_teacher(u)]

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

            StudentProjectMembership.objects.filter(project=updated_project).delete()
            for sid in student_ids:
                StudentProjectMembership.objects.create(student_id=sid, project=updated_project)

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


class TrackProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        print("🔍 Project GET request received")

        if pk:
            try:
                project = Project.objects.select_related(
                    "plan", "supervisor", "coordinator", "department"
                ).get(pk=pk)
            except Project.DoesNotExist:
                return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

            project_data = ProjectSerializer(project).data

            # Members (supervisor, reader, judges)
            member_roles = ProjectMembership.objects.filter(project=project).select_related("user", "role")
            members_data = [{
                "user_id": m.user.id,
                "username": m.user.username,
                "role": m.role.name,
                "group_id": m.group_id
            } for m in member_roles]

            # 🆕 Students
            student_memberships = StudentProjectMembership.objects.filter(project=project).select_related("student")
            students_data = [{
                "id": sm.student.id,
                "username": sm.student.username,
                "student_id": sm.student.student_id
            } for sm in student_memberships if sm.student]

            # Completion
            completion_status = project.plan.completion_status if hasattr(project, 'plan') and project.plan else None

            # Tasks
            tasks = ProjectTask.objects.filter(project=project)
            tasks_data = [{
                "id": task.id,
                "name": task.name,
                "outputs": task.outputs,
                "goals": task.goals,
                "remaining_tasks": task.remaining_tasks,
                "deliverable_text": task.deliverable_text,
                "deliverable_file": task.deliverable_file.url if task.deliverable_file else None,
                "deadline_days": task.deadline_days,
                "assign_to": task.assign_to.username if task.assign_to else None,
                "task_status": task.task_status,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
            } for task in tasks]

            # Logs
            logs = ProjectLog.objects.filter(project=project).order_by('-timestamp')
            logs_data = [{
                "id": log.id,
                "user": log.user.username if log.user else "Unknown",
                "message": log.message,
                "timestamp": log.timestamp,
                "log_type": log.log_type,
                "attachment": log.attachment.url if log.attachment else None,
            } for log in logs]

            # Feedbacks
            feedbacks = FeedbackExchange.objects.filter(project=project).order_by('-created_at')
            feedbacks_data = [{
                "id": fb.id,
                "feedback_text": fb.feedback_text,
                "sender": fb.sender.username if fb.sender else "Unknown",
                "created_at": fb.created_at,
                "feedback_file": fb.feedback_file.url if fb.feedback_file else None,
            } for fb in feedbacks]

            return Response({
                "project": project_data,
                "members": members_data,
                "students": students_data,  # 🆕 students
                "completion_status": completion_status,
                "tasks": tasks_data,
                "logs": logs_data,
                "feedbacks": feedbacks_data,
            })

        else:
            # 📦 List view (important!)
            user = request.user
            departments_data = []

            if hasattr(user, "coordinator"):
                if user.coordinator.is_super:
                    if user.coordinator.department and user.coordinator.department.college:
                        print(f"✅ User is super coordinator of college {user.coordinator.department.college.name}")
                        projects = Project.objects.filter(
                            department__college=user.coordinator.department.college
                        ).select_related("department").order_by("-id")

                        departments = Department.objects.filter(college=user.coordinator.department.college)
                        departments_data = [{"id": d.id, "name": d.name} for d in departments]
                    else:
                        print("⚠️ Super coordinator but no department or college.")
                        projects = Project.objects.none()
                else:
                    print(f"✅ User is normal coordinator of department {user.coordinator.department.name}")
                    projects = Project.objects.filter(
                        department=user.coordinator.department
                    ).select_related("department").order_by("-id")
            else:
                print("⚠️ User is NOT a coordinator.")
                projects = Project.objects.none()

            # ❗ You forgot this before:
            projects_data = ProjectSerializer(projects, many=True).data
            return Response({
                "projects": projects_data,
                "departments": departments_data,
            })
