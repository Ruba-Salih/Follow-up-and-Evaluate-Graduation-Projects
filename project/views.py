from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ProjectProposal, FeedbackExchange
from .serializers import ProjectProposalSerializer, FeedbackExchangeSerializer
from users.serializers import StudentSerializer
from university.models import College, Department
from users.models import Student, Supervisor, Coordinator
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

    # Get feedbacks related to the current user’s proposals
    feedbacks = FeedbackExchange.objects.filter(proposal__in=proposals)

    # Build a dictionary: proposal_id -> feedback_text
    feedback_map = {}
    for fb in feedbacks:
        feedback_map[fb.proposal_id] = fb.feedback_text

    # ✅ Attach the feedback to each proposal directly
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
        "proposals": proposals
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

# If coordinator, check if super or matches department
                if is_coordinator:
                    if user.coordinator.is_super or (proposal.department == user.coordinator.department):
                        pass  # Allow
                    elif not is_owner and not is_recipient:
                        return Response({'detail': 'Unauthorized access.'}, status=403)
                elif not is_owner and not is_recipient:
                    return Response({'detail': 'Unauthorized access.'}, status=403)

                serializer = ProjectProposalSerializer(proposal)
                response_data = serializer.data

            # ✅ Include feedback addressed to the student OR to all (receiver=None)
                feedback_qs = FeedbackExchange.objects.filter(
                    proposal=proposal
                ).filter(
                    Q(receiver=proposal.submitted_by) | Q(receiver__isnull=True)
                ).order_by("-created_at")

                feedback_text = feedback_qs.first().feedback_text if feedback_qs.exists() else None
                response_data["teacher_feedback"] = feedback_text

                return Response(response_data)

            except ProjectProposal.DoesNotExist:
                return Response({'detail': 'Proposal not found.'}, status=404)

    # ⬇️ List view (all proposals for user)
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

        if hasattr(user, 'student') and user.student.department and user.student.department.college:
            college = user.student.department.college
            students = Student.objects.filter(department__college=college).exclude(id=user.student.id)
            students_data = StudentSerializer(students, many=True).data

        # Teachers = users who are not student, coordinator, admin, or superuser
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

        return Response({
            'proposals': proposals_serializer.data,
            'students': students_data,
            'teachers': teachers_data,
            'coordinators': coordinators_data
        })


    def post(self, request):
        user = request.user

    # ❌ Coordinators are not allowed to create proposals
        if hasattr(user, 'coordinator'):
            return Response({'detail': 'Coordinators cannot submit proposals.'}, status=403)

        data = request.data.copy()

    # 🔹 Set department for students or teachers
        if hasattr(user, 'student'):
            if user.student.department:
                data['department'] = user.student.department.id
            else:
                return Response({'detail': 'Student has no department.'}, status=400)
        # Remove unauthorized status fields
            data.pop("teacher_status", None)
            data.pop("coordinator_status", None)

        elif is_teacher(user):
            if 'department' in data:
                data['department'] = int(data['department'])
            else:
                return Response({'detail': 'Department is required for teachers.'}, status=400)
            data.pop("teacher_status", None)
            data.pop("coordinator_status", None)

    # 🔹 Handle proposed_to field
        proposed_to_id = data.get('proposed_to')
        User = get_user_model()
        proposed_user = None
        if proposed_to_id:
            try:
                proposed_user = User.objects.get(id=proposed_to_id)
            except User.DoesNotExist:
                return Response({'detail': 'Proposed recipient not found.'}, status=400)

    # 🔹 Handle team members
        team_members_ids = request.data.getlist("team_members_ids")

    # 🔹 Validate and save proposal
        serializer = ProjectProposalSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            proposal = serializer.save(submitted_by=user, proposed_to=proposed_user)
            if team_members_ids:
                proposal.team_members.set(team_members_ids)
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
            # Prevent students from updating any status field
            data.pop("teacher_status", None)
            data.pop("coordinator_status", None)

        team_members_ids = request.data.getlist("team_members_ids")
        if team_members_ids:
            proposal.team_members.set(team_members_ids)

        # Apply updates manually
        for field, value in update_fields.items():
            setattr(proposal, field, value)

        # Reassign proposed_to if needed
        if proposed_user:
            proposal.proposed_to = proposed_user

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
            # Teachers, coordinators, admins see what they sent
            feedbacks = FeedbackExchange.objects.filter(sender=user).order_by("-created_at")

        serializer = FeedbackExchangeSerializer(feedbacks, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user

        if not is_teacher(user):
            return Response({"detail": "Only teachers can send feedback."}, status=403)

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
