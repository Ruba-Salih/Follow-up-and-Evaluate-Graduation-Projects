from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import ProjectFeedback, FeedbackFile, FeedbackReply
from project.models import Project, StudentProjectMembership, ProjectMembership
from users.services import is_teacher
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import F
from users.models import Coordinator
User = get_user_model()

from django.views.decorators.http import require_GET
from django.utils.timezone import localtime

@login_required
@require_GET
def get_project_feedbacks(request):
    project_id = request.GET.get('project_id')

    if not project_id:
        return JsonResponse({'error': 'Missing project_id'}, status=400)

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)

    feedbacks = ProjectFeedback.objects.filter(project=project).order_by('-created_at')

    results = []
    for fb in feedbacks:
        results.append({
            'id': fb.id,
            'sender_name': fb.sender.get_full_name() or fb.sender.username,
            'message': fb.message,
            'created_at': localtime(fb.created_at).isoformat(),
            'reply': {
                'message': fb.reply.message,
                'created_at': localtime(fb.reply.created_at).isoformat()
            } if hasattr(fb, 'reply') else None
        })

    return JsonResponse(results, safe=False)

@require_POST
@login_required
def submit_feedback_json(request):
    import json
    from django.views.decorators.csrf import csrf_exempt

    try:
        data = json.loads(request.body)
        project_id = data.get("project_id")
        message = data.get("message")

        if not project_id or not message:
            return JsonResponse({"error": "Missing project_id or message"}, status=400)

        project = Project.objects.get(id=project_id)

        feedback = ProjectFeedback.objects.create(
            project=project,
            sender=request.user,
            teacher=request.user,  # or use logic to set teacher properly
            title="",
            message=message
        )

        return JsonResponse({
            "success": True,
            "id": feedback.id,
            "message": feedback.message,
            "created_at": feedback.created_at.isoformat(),
            "sender_name": request.user.get_full_name() or request.user.username
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def review_exchanges(request):
    # Get student's project
    try:
        student_membership = StudentProjectMembership.objects.get(student=request.user)
        project = student_membership.project
    except StudentProjectMembership.DoesNotExist:
        project = None

    # Teachers list for student to send feedback to
    teachers = [user for user in User.objects.all() if is_teacher(user)]

    filtered_feedbacks = []

    if is_teacher(request.user):
        feedbacks = ProjectFeedback.objects.filter(teacher=request.user)

        for feedback in feedbacks:
            # Filter files to only include those where 'reply' is null (student files)
            student_files = feedback.files.filter(reply__isnull=True)
            filtered_feedbacks.append({
                'feedback': feedback,
                'student_files': student_files
            })
    else:

        # Get all student user accounts in the project
        student_users = project.student_memberships.all().values_list('student', flat=True)

        feedbacks = ProjectFeedback.objects.filter(
            Q(project=project, sender=F('teacher')) |
            Q(project=project, sender__in=student_users)
        ).distinct().order_by('-created_at')

        for feedback in feedbacks:
            # Filter files to only include those where 'reply' is null (student files)
            student_files = feedback.files.filter(reply__isnull=True)
            filtered_feedbacks.append({
                'feedback': feedback,
                'student_files': student_files
            })

    error = None  
    # Handle feedback submission by student
    if request.method == 'POST' and not is_teacher(request.user):
        print("POST received for student")
        teacher_id = request.POST.get('teacher')
        title = request.POST.get('title')
        message = request.POST.get('message')
        files = request.FILES.getlist('files')

        if teacher_id and title and message and project:
            try:
                teacher = User.objects.get(id=teacher_id)
                feedback = ProjectFeedback.objects.create(
                    project=project,
                    sender=request.user,  # The student is the sender
                    teacher=teacher,  # The teacher is now the recipient
                    title=title,
                    message=message
                )

                for file in files:
                    FeedbackFile.objects.create(
                        feedback=feedback,
                        file=file
                    )

                return redirect('review-exchanges')

            except (User.DoesNotExist, ValueError):
                error = "Invalid teacher selected."

        else:
            error = "Please fill in all required fields."

    return render(request, 'feedbacks/review_exchanges_student.html', {
        'filtered_feedbacks': filtered_feedbacks,
        'teachers': teachers,
        'error': error
    })


User = get_user_model()

@login_required
def teacher_review_exchanges(request):
    user = request.user
    department = user.department
    college = department.college

    # 1) Projects in this college (for the “project” scenario)
    college_projects = Project.objects.filter(department__college=college)

    # 2) Projects this teacher actually belongs to (for the “coord” scenario)
    teacher_project_ids = ProjectMembership.objects\
                            .filter(user=user)\
                            .values_list('project_id', flat=True)
    teacher_projects = Project.objects.filter(id__in=teacher_project_ids)

    # 3) All coordinators
    coordinators = User.objects.filter(id__in=Coordinator.objects.values_list('id', flat=True))
    # 4) Feedbacks this teacher is the “teacher” for
    filtered_feedbacks = []
    if is_teacher(user):
        qs = ProjectFeedback.objects.filter(
            Q(teacher=user) | Q(sender=user)
        ).order_by('-created_at')
        for fb in qs:
            student_files = fb.files.filter(reply__isnull=True)
            filtered_feedbacks.append({
                'feedback': fb,
                'student_files': student_files,
            })

    error = None

    # 5) Handle the form POST
    if request.method == 'POST':
        recipient_type  = request.POST.get('recipient_type')   # "project" or "coordinator"
        project_id      = request.POST.get('project_id')
        coordinator_id  = request.POST.get('coordinator_id')
        title           = request.POST.get('title')
        message         = request.POST.get('message')
        files           = request.FILES.getlist('files')
        

        # Basic validation
        if recipient_type not in ('project', 'coordinator'):
            error = "You must choose whether to send to a project or a coordinator."
        elif not title or not message:
            error = "Please fill in both title and message."

        # Resolve project and “teacher” user
        if not error:
            # Project scenario
            if recipient_type == 'project':
                try:
                    project_obj = college_projects.get(id=project_id)
                except Project.DoesNotExist:
                    error = "Invalid project selected."
                teacher_user = user

            # Coordinator scenario
            else:
                if not coordinator_id:
                    error = "Please select a coordinator."
                else:
                    print("here we are")
                    teacher_user = get_object_or_404(Coordinator, id=coordinator_id)

                try:
                    project_obj = teacher_projects.get(id=project_id)
                    print("all good")
                except Project.DoesNotExist:
                    error = "Invalid project for coordinator scenario."

        # If all good, create the feedback + files
        if not error:
            print("finally")
            fb = ProjectFeedback.objects.create(
                project=project_obj,
                sender=user,
                teacher=teacher_user,
                title=title,
                message=message
            )
            for f in files:
                FeedbackFile.objects.create(feedback=fb, file=f)
            print("yaay")
            return redirect('teacher-review-exchanges')

    # 6) Render
    return render(request, 'feedbacks/review_exchanges_teacher.html', {
        'college_projects':   college_projects,
        'teacher_projects':   teacher_projects,
        'coordinators':       coordinators,
        'filtered_feedbacks': filtered_feedbacks,
        'error':              error,
    })

@login_required
def coord_review_exchanges(request):
    teachers = [user for user in User.objects.all() if is_teacher(user)]
    selected_teacher = request.GET.get('teacher_id')
    selected_project_id = request.GET.get('project_id')
    filtered_feedbacks = []
    projects = []
    error = None

    if selected_teacher:
        teacher = get_object_or_404(User, id=selected_teacher)
        memberships = ProjectMembership.objects.filter(user=teacher)
        projects = [m.project for m in memberships]


    if hasattr(request.user, 'coordinator'):
        print("yes")
        feedbacks = ProjectFeedback.objects.filter(
            Q(teacher=request.user) | Q(sender=request.user)
        ).order_by('-created_at')

        for feedback in feedbacks:
            teacher_files = feedback.files.filter(reply__isnull=True)
            filtered_feedbacks.append({
                'feedback': feedback,
                'teacher_files': teacher_files
            })

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        project_id = request.POST.get('project')
        title = request.POST.get('title')
        message = request.POST.get('message')
        files = request.FILES.getlist('files')

        if teacher_id and project_id and title and message:
            try:
                teacher = User.objects.get(id=teacher_id)
                project = Project.objects.get(id=project_id)

                feedback = ProjectFeedback.objects.create(
                    project=project,
                    sender=request.user,
                    teacher=teacher,
                    title=title,
                    message=message
                )

                for file in files:
                    FeedbackFile.objects.create(
                        feedback=feedback,
                        file=file
                    )
                return redirect('coord-review-exchanges')
            except (User.DoesNotExist, Project.DoesNotExist, ValueError):
                error = "Invalid teacher or project selected."
        else:
            error = "Please fill in all required fields."
    print(f"filtered feedbacks are: {filtered_feedbacks}")
    return render(request, 'feedbacks/review_exchanges_coord.html', {
        'teachers': teachers,
        'projects': projects,
        'selected_teacher': selected_teacher,
        'selected_project_id': selected_project_id,
        'filtered_feedbacks': filtered_feedbacks,
        'error': error,
    })



@login_required
@require_POST
def reply_to_feedback(request):
    original_feedback_id = request.POST.get('original_feedback_id')
    message = request.POST.get('message')
    files = request.FILES.getlist('files')

    # If missing data, just bounce back
    if not original_feedback_id or not message:
        return _redirect_by_role(request.user)

    # Fetch the feedback (404 if not found)
    feedback_obj = get_object_or_404(ProjectFeedback, id=original_feedback_id)

    # Check role
    user = request.user
    is_teacher_user = is_teacher(user)
    is_coordinator = hasattr(user, 'coordinator')

    if not (is_teacher_user or is_coordinator):
        # Neither teacher nor coordinator: no reply allowed
        return _redirect_by_role(user)

    # Create the reply
    reply = FeedbackReply.objects.create(
        feedback=feedback_obj,
        message=message,
    )

    # Attach any uploaded files
    for f in files:
        FeedbackFile.objects.create(
            feedback=feedback_obj,  # link back to the original feedback
            reply=reply,
            file=f
        )
    print("done")
    # Redirect based on role
    return _redirect_by_role(user)


def _redirect_by_role(user):
    """
    Helper to choose the correct 'review-exchanges' URL name
    based on whether the user is a coordinator, teacher, or student.
    """
    if hasattr(user, 'coordinator'):
        return redirect('coord-review-exchanges')
    if is_teacher(user):
        return redirect('teacher-review-exchanges')
    return redirect('review-exchanges')


@login_required
def delete_feedback(request, id):
    print("hey from delete view")
    feedback = get_object_or_404(ProjectFeedback, id=id)
    user = request.user

    # Determine user role
    is_teacher_user = is_teacher(user)
    is_coordinator = hasattr(user, 'coordinator')

    # Check if user is the sender
    is_sender = feedback.sender == user

    if not is_sender:
        # Students must be project members
        if not is_teacher_user and not is_coordinator:
            is_member = StudentProjectMembership.objects.filter(project=feedback.project, student=user).exists()
            if not is_member:
                print("Student not part of the project.")
                return redirect('review-exchanges')

        else:
            # Teachers/Coordinators can't delete others' feedback
            print("Cross-role or unauthorized delete attempt.")
            return redirect(
                'coord-review-exchanges' if is_coordinator else
                'teacher-review-exchanges'
            )

    # Delete reply and attached files
    if hasattr(feedback, 'reply'):
        feedback.reply.files.all().delete()
        feedback.reply.delete()

    feedback.files.all().delete()
    feedback.delete()

    if is_coordinator:
        return redirect('coord-review-exchanges')
    elif is_teacher_user:
        return redirect('teacher-review-exchanges')
    else:
        return redirect('review-exchanges')


@login_required
def edit_feedback(request, id):
    print("hello from edit view")
    feedback = get_object_or_404(ProjectFeedback, id=id)
    user = request.user

    is_sender = feedback.sender == user
    is_coordinator_user = hasattr(user, 'coordinator')
    is_teacher_user = is_teacher(user)
    is_student_user = not is_teacher_user and not is_coordinator_user

    # Prevent cross-role editing unless coordinator or sender
    if not is_sender and not is_coordinator_user and not is_student_user:
        print("Unauthorized access: not the sender or coordinator.")
        return redirect('review-exchanges')

    # If student, ensure they are part of the project
    if is_student_user:
        is_member = StudentProjectMembership.objects.filter(project=feedback.project, student=user).exists()
        if not is_member:
            print("Student not part of the project.")
            return redirect('review-exchanges')

    error = None

    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        files = request.FILES.getlist('files')

        if title and message:
            feedback.title = title
            feedback.message = message
            feedback.save()

            # Delete marked files
            delete_file_ids = request.POST.getlist('delete_files')
            print(f"File IDs to delete: {delete_file_ids}")
            if delete_file_ids:
                FeedbackFile.objects.filter(id__in=delete_file_ids, feedback=feedback).delete()

            # Add new files
            for file in files:
                FeedbackFile.objects.create(feedback=feedback, file=file)

            print("Edit completed successfully")
            if is_coordinator_user:
                return redirect('coord-review-exchanges')
            elif is_teacher_user:
                return redirect('teacher-review-exchanges')
            else:
                return redirect('review-exchanges')

        else:
            error = 'Title and message are required.'

    return render(request, 'feedbacks/edit_feedback.html', {
        'feedback': feedback,
        'error': error
    })


@login_required
def edit_feedback_reply(request, reply_id):
    reply = get_object_or_404(FeedbackReply, id=reply_id)
    feedback = reply.feedback

    user = request.user
    is_teacher_user = is_teacher(user)
    is_coordinator = hasattr(user, 'coordinator')

    # Only teachers and coordinators may edit replies
    if not (is_teacher_user or is_coordinator):
        # send everyone else back to their respective listing
        if is_coordinator:
            return redirect('coord-review-exchanges')
        if is_teacher_user:
            return redirect('teacher-review-exchanges')
        return redirect('review-exchanges')

    error = None

    if request.method == 'POST':
        message = request.POST.get('message')
        # note the form field name is files[] so getlist('files[]')
        files = request.FILES.getlist('files[]')

        if not message:
            error = "Message is required."
        else:
            # update text
            reply.message = message
            reply.save()

            # delete any files the user checked for removal
            delete_ids = request.POST.getlist('delete_files')
            if delete_ids:
                FeedbackFile.objects.filter(
                    id__in=delete_ids,
                    feedback=feedback,
                    reply=reply
                ).delete()

            # add any newly uploaded files
            for f in files:
                FeedbackFile.objects.create(
                    feedback=feedback,
                    reply=reply,
                    file=f
                )

            # redirect back to teacher or coordinator listing
            return redirect('coord-review-exchanges' if is_coordinator else 'teacher-review-exchanges')

    return render(request, 'feedbacks/edit_reply.html', {
        'reply': reply,
        'feedback': feedback,
        'error': error,
    })

def get_teacher_projects(request, teacher_id):
    try:
        memberships = ProjectMembership.objects.filter(user_id=teacher_id)
        project_ids = memberships.values_list('project_id', flat=True)

        # Check for debugging
        print("Teacher ID:", teacher_id)
        print("Memberships:", memberships)
        print("Project IDs:", list(project_ids))

        projects = Project.objects.filter(id__in=project_ids).values('id', 'name')
        return JsonResponse({'projects': list(projects)})
    except Exception as e:
        print("Error in get_teacher_projects:", e)  # <== Log the actual error
        return JsonResponse({'error': str(e)}, status=500)