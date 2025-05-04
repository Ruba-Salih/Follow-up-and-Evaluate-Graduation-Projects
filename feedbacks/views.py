from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import ProjectFeedback, FeedbackFile, FeedbackReply
from project.models import Project, StudentProjectMembership
from users.services import is_teacher
from django.views.decorators.http import require_POST

User = get_user_model()


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
        # Feedbacks related to this student (as sender or receiver)
        sent_feedbacks = ProjectFeedback.objects.filter(sender=request.user)
        feedbacks = ProjectFeedback.objects.filter(project=project).order_by('-created_at')

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

        print(f"teacher: {teacher_id}, title is: {title}, message is: {message}, files are: {files}")
        if teacher_id and title and message and project:
            print("hey data are there")
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


@login_required
def teacher_review_exchanges(request):
    print("hello from the view")
    user = request.user

    # project list for teacher to send feedback to
    department = user.department
    print(f"department: {department}]")
    college = department.college
    print(f"collage: {college}]")
    projects = Project.objects.filter(department__college=college)
    print(f"projects are: {projects}")

    filtered_feedbacks = []

    if is_teacher(request.user):
        feedbacks = ProjectFeedback.objects.filter(teacher=request.user).order_by('-created_at')

        for feedback in feedbacks:
            student_files = feedback.files.filter(reply__isnull=True)
            filtered_feedbacks.append({
                'feedback': feedback,
                'student_files': student_files
            })

    error = None
    if request.method == 'POST':
        print("POST received for teacher")
        teacher = request.user
        project_id = request.POST.get('project')
        title = request.POST.get('title')
        message = request.POST.get('message')
        files = request.FILES.getlist('files')

        print(f"teacher: {teacher}, title: {title}, message: {message}, files: {files}")

        try:
            project_obj = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            error = "Invalid project selected."
            return render(request, 'feedbacks/review_exchanges_teacher.html', {'error': error})

        if teacher and title and message and project_obj:
            print("data are valid")
            try:
                feedback = ProjectFeedback.objects.create(
                    project=project_obj,
                    sender=teacher,
                    teacher=teacher,
                    title=title,
                    message=message
                )

                if files:
                    for file in files:
                        FeedbackFile.objects.create(
                            feedback=feedback,
                            file=file
                        )

                return redirect('teacher-review-exchanges')

            except Exception as e:
                print(f"Error: {str(e)}")
                error = "There was an error submitting your feedback."

        else:
            error = "Please fill in all required fields."

    return render(request, 'feedbacks/review_exchanges_teacher.html', {
        'filtered_feedbacks': filtered_feedbacks,
        'projects': projects,
        'error': error
    })


@login_required
@require_POST
def reply_to_feedback(request):
    # Get the original feedback ID, message, and files
    original_feedback_id = request.POST.get('original_feedback_id')
    message = request.POST.get('message')
    files = request.FILES.getlist('files')

    if not original_feedback_id or not message:
        return redirect('teacher-review-exchanges')  # or show an error message if needed

    try:
        # Fetch the original feedback that the teacher is replying to
        original_feedback = ProjectFeedback.objects.get(id=original_feedback_id)

        # Ensure only a teacher can reply
        if not is_teacher(request.user):
            return redirect('teacher-review-exchanges')

        # Create a new reply for the feedback
        reply = FeedbackReply.objects.create(
            feedback=original_feedback,  # Link the reply to the original feedback
            message=message
        )

        # Attach files to the reply
        for file in files:
            FeedbackFile.objects.create(
                feedback=original_feedback,  # The original feedback
                reply=reply,  # Attach the file to the reply
                file=file
            )

    except ProjectFeedback.DoesNotExist:
        pass  # Optional error handling if the feedback does not exist

    return redirect('teacher-review-exchanges')


@login_required
def delete_feedback(request, id):
    print("hey from delete view")
    feedback = get_object_or_404(ProjectFeedback, id=id)

    if is_teacher(feedback.sender) != is_teacher(request.user):
        print("Cross-role editing not allowed.")
        return redirect('review-exchanges' if not is_teacher(request.user) else 'teacher-review-exchanges')

    # For students, also confirm they're members of the project
    project = feedback.project
    is_member = StudentProjectMembership.objects.filter(project=project, student=request.user).exists()
    if not is_member and not is_teacher(request.user):
        print("Student not part of the project.")
        return redirect('review-exchanges' if not is_teacher(request.user) else 'teacher-review-exchanges')

    # Delete associated reply and files
    if hasattr(feedback, 'reply'):
        feedback.reply.files.all().delete()
        feedback.reply.delete()

    feedback.files.all().delete()
    feedback.delete()
    return redirect('review-exchanges' if not is_teacher(request.user) else 'teacher-review-exchanges')


@login_required
def edit_feedback(request, id):
    print("hello from edit view")
    feedback = get_object_or_404(ProjectFeedback, id=id)


    if is_teacher(feedback.sender) != is_teacher(request.user):
        print("Cross-role editing not allowed.")
        return redirect('review-exchanges' if not is_teacher(request.user) else 'teacher-review-exchanges')

    # For students, also confirm they're members of the project
    project = feedback.project
    is_member = StudentProjectMembership.objects.filter(project=project, student=request.user).exists()
    if not is_member and not is_teacher(request.user):
        print("Student not part of the project.")
        return redirect('review-exchanges' if not is_teacher(request.user) else 'teacher-review-exchanges')


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
            print(f"file ides are: {delete_file_ids}")
            if delete_file_ids:
                print("im deleting")
                FeedbackFile.objects.filter(id__in=delete_file_ids, feedback=feedback).delete()

            for file in files:
                FeedbackFile.objects.create(
                    feedback=feedback,
                    file=file
                )
            print("going well")
            return redirect('review-exchanges' if not is_teacher(request.user) else 'teacher-review-exchanges')
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

    # Only teacher who sent the reply can edit
    if  not is_teacher(request.user):
        return redirect('teacher-review-exchanges')

    error = None

    if request.method == 'POST':
        message = request.POST.get('message')
        files = request.FILES.getlist('files[]')

        if message:
            reply.message = message
            reply.save()

             # Delete marked files
            delete_file_ids = request.POST.getlist('delete_files')
            print(f"file ides are: {delete_file_ids}")
            if delete_file_ids:
                print("im deleting")
                FeedbackFile.objects.filter(id__in=delete_file_ids, feedback=feedback).delete()

            # Add new files to the reply
            for file in files:
                FeedbackFile.objects.create(feedback=feedback, reply=reply, file=file)

            return redirect('teacher-review-exchanges')
        else:
            error = "Message is required."

    return render(request, 'feedbacks/edit_reply.html', {
        'reply': reply,
        'feedback': feedback,
        'error': error
    })

""" 
@login_required
def delete_feedback(request, id):
    print("hey from delete view")
    feedback = get_object_or_404(ProjectFeedback, id=id)
    
    project = feedback.project  # Assuming Feedback model has a FK to Project
    is_member = StudentProjectMembership.objects.filter(project=project, student=request.user).exists()

    if feedback.sender != request.user and not is_member:
        return redirect('review-exchanges' if not is_teacher(request.user) else 'teacher-review-exchanges')


    # Only the sender (student or teacher) can delete it
    if feedback.sender != request.user and not is_member:
        print(f"you are not allowed feedback sender: {feedback.sender}, and user {request.user}")
        return redirect('review-exchanges' if not is_teacher(request.user) else 'teacher-review-exchanges')

    # Delete associated reply and files
    if hasattr(feedback, 'reply'):
        feedback.reply.files.all().delete()
        feedback.reply.delete()

    feedback.files.all().delete()
    feedback.delete()
    return redirect('review-exchanges' if not is_teacher(request.user) else 'teacher-review-exchanges')


@login_required
def edit_feedback(request, id):
    print("hello from the view")
    feedback = get_object_or_404(ProjectFeedback, id=id)
    
    project = feedback.project  # Assuming Feedback model has a FK to Project
    is_member = StudentProjectMembership.objects.filter(project=project, student=request.user).exists()
    print(is_member)
    if feedback.sender != request.user and not is_member:
        return redirect('review-exchanges' if not is_teacher(request.user) else 'teacher-review-exchanges')

    error = None

    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        files = request.FILES.getlist('files')  # Get uploaded files

        if title and message:
            feedback.title = title
            feedback.message = message
            feedback.save()

            for file in files:
                FeedbackFile.objects.create(
                    feedback=feedback,
                    file=file
                )
            print("going well")
            return redirect('review-exchanges' if not is_teacher(request.user) else 'teacher-review-exchanges')
        else:
            error = 'Title and message are required.'

    return render(request, 'feedbacks/edit_feedback.html', {
        'feedback': feedback,
        'error': error
    })
 """