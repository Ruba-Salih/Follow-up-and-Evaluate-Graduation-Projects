from django.shortcuts import render, redirect
from django.shortcuts import  get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import AvailableTime, Meeting, MeetingParticipant, MeetingFile
from .serializers import AvailableTimeSerializer, MeetingRequestSerializer, MeetingSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import json
from django.http import HttpResponseNotFound
import logging
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.utils import timezone
from project .models import Project, StudentProjectMembership
from users.services import is_teacher
from django.views import View
from notifications.models import Notification
from notifications.constants import MEETING_DECLINED, MEETING_ACCEPT, MEETING_REQUEST, MEETING_RECOMMENDATION
from rest_framework import pagination
from users.models import User
from django.http import HttpResponseNotFound
from django.db.models import Q



User = get_user_model()

# ------------------- API VIEWS -------------------

@method_decorator(csrf_exempt, name='dispatch')
class SetAvailableTimeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        available_times = AvailableTime.objects.filter(user=request.user)
        serializer = AvailableTimeSerializer(available_times, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AvailableTimeSerializer(data=request.data, many=True)
        if serializer.is_valid():
            print("hey")
            created_slots = []
            for item in serializer.validated_data:
                # Check if this slot already exists for the user
                existing_slot = AvailableTime.objects.filter(
                    user=request.user,
                    day=item['day'],
                    start_time=item['start_time'],
                    end_time=item['end_time']
                ).first()
                
                if existing_slot:
                    print("hey it already there")
                    return Response({'error': f"Slot already exists for {item['day']} at {item['start_time']}-{item['end_time']}"}, status=status.HTTP_400_BAD_REQUEST)

                obj = AvailableTime.objects.create(
                    user=request.user,
                    day=item['day'],
                    start_time=item['start_time'],
                    end_time=item['end_time']
                )
                created_slots.append(obj)
            return Response(AvailableTimeSerializer(created_slots, many=True).data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def delete_available_time(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        day = data.get('day')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        try:
            obj = AvailableTime.objects.get(
                user=request.user,
                day=day,
                start_time=start_time,
                end_time=end_time
            )
            obj.delete()
            return JsonResponse({'message': 'Deleted'})
        except AvailableTime.DoesNotExist:
            return JsonResponse({'error': 'Time slot not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)


class TeacherListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        teachers = [user for user in User.objects.all().order_by('id') if is_teacher(user)]
        
        # Apply pagination
        paginator = pagination.PageNumberPagination()
        paginator.page_size = 10  # ✅ ensure this is set

        paginated_teachers = paginator.paginate_queryset(teachers, request)

        if paginated_teachers is None:
            return Response({"error": "Pagination failed."}, status=400)

        data = [
            {"id": teacher.id, "name": teacher.get_full_name() or teacher.username}
            for teacher in paginated_teachers
        ]
        return paginator.get_paginated_response(data)


class TeacherAvailableTimeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        print("HIT TEACHER AVAILABILITY ENDPOINT")
        teacher_id = request.query_params.get('teacher_id')
        selected_date = request.query_params.get('date')

        if not teacher_id or not selected_date:
            return Response({'error': 'teacher_id and date are required.'}, status=400)

        try:
            teacher = User.objects.get(id=teacher_id)
        except User.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=404)

        try:
            selected_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        # Map the full weekday name to the abbreviated form
        weekday_map = {
            'Monday': 'mon',
            'Tuesday': 'tue',
            'Wednesday': 'wed',
            'Thursday': 'thu',
            'Friday': 'fri',
            'Saturday': 'sat',
            'Sunday': 'sun',
        }

        weekday = selected_date.strftime('%A')  # Get full weekday name (e.g., "Monday")
        weekday_abbr = weekday_map.get(weekday)  # Map to abbreviated form (e.g., "mon")

        if not weekday_abbr:
            return Response({'error': 'Invalid weekday.'}, status=400)

        now = timezone.now()

        available_blocks = AvailableTime.objects.filter(user=teacher, day=weekday_abbr)
        if not available_blocks.exists():
            return Response([], status=200)

        available_slots = []

        for block in available_blocks:
            block_start = timezone.make_aware(datetime.combine(selected_date, block.start_time))
            block_end = timezone.make_aware(datetime.combine(selected_date, block.end_time))

            if block_end <= now:
                continue

            overlapping_meetings = Meeting.objects.filter(
                teacher=teacher,
                start_datetime__lt=block_end,
                end_datetime__gt=block_start,
            ).exclude(status='pending').order_by('start_datetime')

            free_ranges = []
            current_start = block_start

            if overlapping_meetings.exists():
                for meeting in overlapping_meetings:
                    if meeting.start_datetime > current_start:
                        free_end = meeting.start_datetime
                        if free_end > now:
                            free_ranges.append((current_start, free_end))
                    current_start = max(current_start, meeting.end_datetime)
            

            if current_start < block_end:
                free_ranges.append((current_start, block_end))

            for start, end in free_ranges:
                if end > now and end > start:
                    available_slots.append({
                        'start_time': start.time().strftime('%H:%M'),
                        'end_time': end.time().strftime('%H:%M'),
                        'date': selected_date.isoformat(),
                    })

        return Response(available_slots)



class TeacherMeetingRequestsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        meetings = Meeting.objects.filter(requested_by__in=[teacher.id for teacher in request.user.teachers.all()], status='pending')
        serializer = MeetingRequestSerializer(meetings, many=True)
        return Response(serializer.data)


class ScheduleMeetingView(View):
    def get(self, request):
        if is_teacher(request.user):
            college = request.user.department.college
            projects = Project.objects.filter(department__college=college)
            return render(request, 'meetings/schedule_meeting_teacher.html', {'projects': projects})

        elif hasattr(request.user, 'student'):
            return render(request, 'meetings/schedule_meeting_student.html')

        else:
            return redirect('landing-page')


class ScheduleMeetingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print("heelo from tthe view")
        teacher_id = request.data.get('teacher_id')
        day = request.data.get('day')
        meeting_date = request.data.get('meeting_date')
        slot_start_time = request.data.get('slot_start_time')
        slot_end_time = request.data.get('slot_end_time')
        meeting_start_time = request.data.get('meeting_start_time')
        meeting_end_time = request.data.get('meeting_end_time')
        comment = request.data.get('comment')

        print(f"times are{slot_start_time} - {slot_end_time} and {meeting_start_time} - {meeting_end_time}")

        if not teacher_id or not slot_start_time or not slot_end_time:
            print("missing")
            return Response({'error': 'Missing required fields.'}, status=400)
        
        if not is_teacher(request.user):
            print("hello student")
            meeting_start_obj = datetime.strptime(meeting_start_time, "%H:%M").time()
            meeting_end_obj = datetime.strptime(meeting_end_time, "%H:%M").time()
            slot_start_obj = datetime.strptime(slot_start_time, "%H:%M").time()
            slot_end_obj = datetime.strptime(slot_end_time, "%H:%M").time()

            print(f"Comparing meeting time {meeting_start_obj} - {meeting_end_obj} with slot {slot_start_obj} - {slot_end_obj}")

            if meeting_start_obj < slot_start_obj or meeting_end_obj > slot_end_obj:
                print("Meeting time outside allowed slot, rejecting...")
                return Response(
                    {'error': 'Meeting time must be within the allowed time slot.'},
                    status=400
                )
            
        if is_teacher(request.user):
            # Parse meeting date and time
            meeting_date_obj = datetime.strptime(meeting_date, "%Y-%m-%d").date()
            meeting_start_obj = datetime.strptime(slot_start_time, "%H:%M").time()
            meeting_end_obj = datetime.strptime(slot_end_time, "%H:%M").time()

            start_datetime = datetime.combine(meeting_date_obj, meeting_start_obj)
            end_datetime = datetime.combine(meeting_date_obj, meeting_end_obj)

            # Get the project ID from the request
            project_id = request.data.get('project_id')
            if not project_id:
                return Response({'error': 'Missing project_id.'}, status=400)

            # Check for conflicting accepted meetings for that project
            conflict_exists = Meeting.objects.filter(
                project_id=project_id,
                status='accepted',
                start_datetime__lt=end_datetime,
                end_datetime__gt=start_datetime
            ).exists()

            if conflict_exists:
                return Response(
                    {'error': 'This group already has a meeting scheduled during this time.'},
                    status=400
                )

        
        try:
            print(f"meeting date is {meeting_date}")
            meeting_date_obj = datetime.strptime(meeting_date, "%Y-%m-%d").date()

            if meeting_start_time and meeting_end_time:
                print(f"meet start at {meeting_start_time} and end at {meeting_end_time}")
                start_hour, start_minute = map(int, meeting_start_time.split(':'))
                end_hour, end_minute = map(int, meeting_end_time.split(':'))

            else:
                # Teacher flow
                start_hour, start_minute = map(int, slot_start_time.split(':'))
                end_hour, end_minute = map(int, slot_end_time.split(':'))

            meeting_start = timezone.make_aware(datetime.combine(meeting_date_obj, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute))
            meeting_end = timezone.make_aware(datetime.combine(meeting_date_obj, datetime.min.time()) + timedelta(hours=end_hour, minutes=end_minute))

        except Exception as e:
            logging.error(f"Error parsing time or date: {e}")
            return Response({'error': 'Invalid time or date format.'}, status=400)

        # Teacher object
        try:
            teacher = User.objects.get(id=teacher_id)
        except User.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=404)

        # Assign project
        if is_teacher(request.user):
            project_id = request.data.get('project_id')
            if not project_id:
                return Response({'error': 'Project field is required for teachers.'}, status=400)

            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return Response({'error': 'Project not found.'}, status=404)
        else:
            membership = StudentProjectMembership.objects.filter(student=request.user, project__isnull=False).first()
            if not membership:
                return Response({'error': 'Student is not part of any project.'}, status=404)
            project = membership.project

       # Create meeting
        meeting = Meeting.objects.create(
            requested_by=request.user,
            teacher=teacher, 
            start_datetime=meeting_start,
            end_datetime=meeting_end,
            status='pending',
            comment=comment,
            project=project 
        )

        #add participants function
        meeting.add_participants()

        # Notifications
        if is_teacher(request.user):  # Teacher scheduling the meeting
            # Notify all students in the project
            students = meeting.project.student_memberships.all()
            for membership in students:
                Notification.objects.create(
                    recipient=membership.student,
                    message=f"Teacher  {request.user.get_full_name()} has requseted a meeting with your group.",
                    notification_type=MEETING_REQUEST
                )
        else:
            Notification.objects.create(
                recipient=meeting.teacher,
                message=f"{request.user.get_full_name()} requested a meeting.",
                notification_type=MEETING_REQUEST
            )
            students = meeting.project.student_memberships.exclude(student=request.user)
            for membership in students:
                Notification.objects.create(
                    recipient=membership.student,
                    message=f"{request.user.get_full_name()} requested a meeting.",
                    notification_type=MEETING_REQUEST
                )

        return Response({'message': 'Meeting request sent successfully!'}, status=201)


class MeetingApprovalAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        meeting_id = request.data.get('meeting_id')
        status = request.data.get('status')

        try:
            meeting = Meeting.objects.get(meeting_id=meeting_id)
            if meeting.status != 'pending':
                return Response({"error": "Meeting already processed."}, status=400)

            if status == 'accepted':
                meeting.status = 'scheduled'
            elif status == 'declined':
                meeting.status = 'cancelled'
            else:
                return Response({"error": "Invalid status."}, status=400)

            meeting.save()

            # Update the status of participants as well if the meeting is accepted
            for participant in meeting.participants.all():
                if participant.user != meeting.requested_by:  # Avoid marking the requester's status
                    participant.has_accepted = status == 'accepted'
                    participant.save()

            return Response({"message": "Meeting status updated successfully."}, status=200)

        except Meeting.DoesNotExist:
            return Response({"error": "Meeting not found."}, status=404)

# views.py
class UpcomingMeetingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_time = timezone.now()
        user = request.user

        if is_teacher(user):
            upcoming_meetings = Meeting.objects.filter(
                teacher=user,
                status='accepted',
                start_datetime__gte=current_time
            ).order_by('start_datetime')
        else:
            project_ids = StudentProjectMembership.objects.filter(
                student=user,
                project__isnull=False
            ).values_list("project__id", flat=True)

            upcoming_meetings = Meeting.objects.filter(
                project__id__in=project_ids,
                status='accepted',
                start_datetime__gte=current_time
            ).order_by('start_datetime')

        serializer = MeetingSerializer(upcoming_meetings, many=True)
        return Response(serializer.data)



# ------------------- PAGE VIEWS -------------------

@login_required
def set_available_time_page(request):
    day_choices = AvailableTime.DAYS_OF_WEEK
    return render(request, 'meetings/set_available_time.html', {'day_choices': day_choices})

@login_required
def meeting_requests_page(request):
    if is_teacher(request.user):  # Teacher
        # Teacher's meetings requested by the teacher (sent by them)
        teacher_requests = Meeting.objects.filter(teacher=request.user, status='pending', requested_by=request.user).order_by('-created_at')
        # Teacher's meetings received (requested by students)
        student_requests = Meeting.objects.filter(teacher=request.user, status='pending').exclude(requested_by=request.user).order_by('-created_at')
        
        context = {
            'user_meeting_requests': teacher_requests,
            'received_meeting_requests': student_requests,
        }
    
    else:  # Student
        # Student's meetings requested by the student (sent by them)
        student_requests = Meeting.objects.filter(requested_by=request.user, status='pending').order_by('-created_at')
        # Student's meetings received (related to their project)
        try:
            memberships = StudentProjectMembership.objects.filter(student=request.user, project__isnull=False)
            project_ids = memberships.values_list("project_id", flat=True)
            project_related_meetings = Meeting.objects.filter(project_id__in=project_ids, status='pending').exclude(requested_by=request.user).order_by('-created_at')
        except StudentProjectMembership.DoesNotExist:
            project_related_meetings = []
        
        context = {
            'user_meeting_requests': student_requests,
            'received_meeting_requests': project_related_meetings,
        }

    return render(request, 'meetings/meeting_requests.html', context)



@login_required
def meeting_history_page(request):

    if is_teacher(request.user):  # Teacher
        # Fetch all meetings where the teacher is the requester and the status is 'accepted' or 'completed'
        meetings = Meeting.objects.filter(teacher=request.user, status__in=['cancelled', 'completed', 'accepted']).order_by('-created_at')
    else:  # Student
        # Fetch all meetings where the student is a member of the project, status is 'canceled' or 'completed', and exclude their own requests
        try:
            memberships = StudentProjectMembership.objects.filter(student=request.user, project__isnull=False)
            projects = [m.project for m in memberships]
            meetings = Meeting.objects.filter(project__in=projects, status__in=['cancelled', 'completed']).order_by('-created_at')
        except StudentProjectMembership.DoesNotExist:
            # If the student is not part of any project, return an empty list
            meetings = []

    # Fetch the files related to each meeting
    meeting_files = {}
    for meeting in meetings:
        files = MeetingFile.objects.filter(meeting=meeting)
        meeting_files[meeting.meeting_id] = files
        print(f"Meeting files for {meeting.meeting_id}: {meeting_files[meeting.meeting_id]}")

    print(meeting_files)
    # Pass the meetings and attendance status for each participant to the template
    meeting_participants = {}
    for meeting in meetings:
        participants = MeetingParticipant.objects.filter(meeting=meeting)
        meeting_participants[meeting.meeting_id] = participants
        print(f"meeting participants are: {meeting_participants}")
    
    # Render the template with the meeting details and participant attendance information
    return render(request, 'meetings/meeting_history.html', {
        'meetings': meetings,
        'meeting_participants': meeting_participants,
        'meeting_files': meeting_files,
        'is_teacher': is_teacher(request.user),
    })


@login_required
def accept_meeting(request, meeting_id):
    try:
        # Get the meeting by ID
        meeting = Meeting.objects.get(meeting_id=meeting_id)
    except Meeting.DoesNotExist:
        return HttpResponseNotFound("Meeting not found")

    user = request.user
    meeting_start = meeting.start_datetime
    meeting_end = meeting.end_datetime

    # Check if the user is a teacher or a student and apply the respective checks
    if is_teacher(user):  # Teacher
        # Check if the teacher already has an accepted meeting during the same time
        conflict = Meeting.objects.filter(
            teacher=user,
            status='accepted',
            start_datetime__lt=meeting_end,  # If the start time of any accepted meeting is before the end time
            end_datetime__gt=meeting_start  # And the end time of any accepted meeting is after the start time
        ).exists()

        if conflict:
            return HttpResponseNotFound("You already have an accepted meeting during this time slot.")

        # Accept the meeting
        meeting.status = 'accepted'
        meeting.save()

        # After accepting, delete any conflicting requested meetings
        Meeting.objects.filter(
            Q(project=meeting.project),
            Q(status='pending'),
            start_datetime__lt=meeting_end,
            end_datetime__gt=meeting_start
        ).delete()

        # Send notifications to students in the project
        students = meeting.project.student_memberships.all()
        for membership in students:
            Notification.objects.create(
                recipient=membership.student,
                message=f"Your meeting request has been accepted by {user.get_full_name()}.",
                notification_type=MEETING_ACCEPT
            )

    else:  # Student
        # Check if the student already has an accepted meeting during the same time
        conflict = Meeting.objects.filter(
            Q(requested_by=user) |  # The user is the one who requested the meeting
            Q(project__student_memberships__student=user),
            status='accepted',  # The meeting must be accepted
            start_datetime__lt=meeting_end,  # Check if the start time is before the requested end time
            end_datetime__gt=meeting_start  # Check if the end time is after the requested start time
        ).exists()

        if conflict:
            return HttpResponseNotFound("You already have an accepted meeting during this time slot.")

        # Accept the meeting
        meeting.status = 'accepted'
        meeting.save()

        # After accepting, delete any conflicting requested meetings
        Meeting.objects.filter(
            Q(project=meeting.project),
            Q(status='pending'),
            start_datetime__lt=meeting_end,
            end_datetime__gt=meeting_start
        ).delete()

        # Notify the teacher about the acceptance
        Notification.objects.create(
            recipient=meeting.teacher,
            message=f"{user.get_full_name()} accepted the meeting.",
            notification_type=MEETING_ACCEPT
        )

        # Notify other students in the same project
        students = meeting.project.student_memberships.exclude(student=user)
        for membership in students:
            Notification.objects.create(
                recipient=membership.student,
                message=f"{user.get_full_name()} accepted the meeting.",
                notification_type=MEETING_ACCEPT
            )

    return redirect('meeting-requests-page')



@login_required
def decline_meeting(request, meeting_id):
    try:
        meeting = Meeting.objects.get(meeting_id=meeting_id)
    except Meeting.DoesNotExist:
        return HttpResponseNotFound("Meeting not found")

    user = request.user

    # Decline the meeting
    meeting.status = 'declined'
    meeting.save()

    # Send notifications
    if is_teacher(user):
        # If the user is a teacher, notify students in the project
        students = meeting.project.student_memberships.all()
        for membership in students:
            Notification.objects.create(
                recipient=membership.student,
                message=f"Your meeting request has been declined by {user.get_full_name()}.",
                notification_type=MEETING_DECLINED
            )
    else:
        # If the user is a student, notify the teacher and other group members
        # Notify the teacher
        Notification.objects.create(
            recipient=meeting.teacher,
            message=f"{user.get_full_name()} declined the meeting.",
            notification_type=MEETING_DECLINED
        )
        # Notify other students in the same project
        students = meeting.project.student_memberships.exclude(student=user)
        for membership in students:
            Notification.objects.create(
                recipient=membership.student,
                message=f"{user.get_full_name()} declined the meeting.",
                notification_type=MEETING_DECLINED
            )

    return redirect('meeting-requests-page')


@login_required
def update_meeting_status(request, meeting_id):
    meeting = get_object_or_404(Meeting, meeting_id=meeting_id)

    if not is_teacher(request.user):
        messages.error(request, "You are not authorized to update this meeting.")
        return redirect('meeting-history-page')

    if request.method == 'POST':
        status = request.POST.get('status')
        new_recommendation = request.POST.get('recommendation')
        files_to_delete = request.POST.getlist('delete_file')

        # Delete the files
        for file_id in files_to_delete:
            file = get_object_or_404(MeetingFile, pk=file_id)
            file.delete()

        files = request.FILES.getlist('meeting_files')
        print(f"files are: {files}")
        for uploaded_file in files:
            print(f"File uploaded: {uploaded_file.name}")
            MeetingFile.objects.create(
                meeting=meeting,
                uploaded_by=request.user,
                file=uploaded_file,
                description=request.POST.get('file_description', '')
            )
            print("finished")
        # Check if a new recommendation was added
        recommendation_was_added = not meeting.recommendation and new_recommendation

        meeting.status = status
        meeting.recommendation = new_recommendation
        meeting.save()

        for participant in meeting.participants.all():
            attended = request.POST.get(f'attendance_{participant.id}')
            participant.attendance_status = 'attended' if attended else 'absent'
            participant.save()

        # Send notification if recommendation was added
        if recommendation_was_added:
            for participant in meeting.participants.all():
                # Send notification logic here (see below)
                Notification.objects.create(
                    recipient=participant.user,
                    message=f"{request.user.get_full_name()} added a recommendation to the meeting on {meeting.start_datetime.strftime('%Y-%m-%d %H:%M')}.",
                    notification_type=MEETING_RECOMMENDATION
                )

        messages.success(request, "Meeting status, attendance, and recommendation updated.")
        return redirect('meeting-history-page')

    return render(request, 'meetings/meeting_requests.html', {'meeting': meeting})

@login_required
def delete_meeting(request, meeting_id):
    try:
        # Fetch the meeting by ID
        meeting = Meeting.objects.get(meeting_id=meeting_id)
    except Meeting.DoesNotExist:
        return HttpResponseNotFound("Meeting not found")
    
    user = request.user
    if is_teacher(user):  # Teacher
        if meeting.teacher == request.user:  # Only allow deletion if the teacher is the creator
            meeting.delete()
            return redirect('meeting-requests-page')
        else:
            return HttpResponseForbidden("You do not have permission to delete this meeting.")

    else:  # Student
        try:
            memberships = StudentProjectMembership.objects.filter(student=request.user, project=meeting.project)
            if memberships.exists() and meeting.requested_by == request.user:
                # Only allow deletion if the meeting is related to the student's project and the student created it
                meeting.delete()
                return redirect('meeting-requests-page')
            else:
                return HttpResponseForbidden("You do not have permission to delete this meeting.")
        except StudentProjectMembership.DoesNotExist:
            return HttpResponseForbidden("You are not part of any project, and cannot delete this meeting.")


@login_required
def submit_meeting_report(request, meeting_id):
    meeting = get_object_or_404(Meeting, meeting_id=meeting_id)

    if meeting.status != 'completed':
        messages.error(request, "You can only submit a report for completed meetings.")
        return redirect('meeting-history-page')

    # Only students in the meeting can submit
    if not meeting.participants.filter(user=request.user).exists():
        messages.error(request, "You are not a participant of this meeting.")
        return redirect('meeting-history-page')

    if request.method == 'POST':
        report = request.POST.get('report')
        if not report:
            messages.error(request, "Report text cannot be empty.")
            return redirect('submit-meeting-report', meeting_id=meeting.id)

        files_to_delete = request.POST.getlist('delete_file')

        # Delete the files
        for file_id in files_to_delete:
            file = get_object_or_404(MeetingFile, pk=file_id)
            file.delete()
        # Save report
        meeting.meeting_report = report
        meeting.save()

        # Handle file uploads
        files_uploaded = False
        for uploaded_file in request.FILES.getlist('meeting_files'):
            MeetingFile.objects.create(
                meeting=meeting,
                uploaded_by=request.user,
                file=uploaded_file,
                description=request.POST.get('file_description', '')
            )
            files_uploaded = True

        if files_uploaded:
            messages.success(request, "Meeting report and files submitted successfully.")
        else:
            messages.success(request, "Meeting report submitted successfully without files.")

        return redirect('meeting-history-page')

    return render(request, 'meetings/submit_report.html', {'meeting': meeting})

@login_required
def edit_meeting_file(request, file_id):
    file = get_object_or_404(MeetingFile, id=file_id)
    if request.user != file.uploaded_by:
        messages.error(request, "You are not allowed to edit this file.")
        return redirect('meeting-history-page')
    
    if request.method == 'POST':
        file.description = request.POST.get('file_description', '')
        file.save()
        messages.success(request, "File description updated.")
    
    return redirect('meeting-history-page')

@login_required
def delete_meeting_file(request, file_id):
    file = get_object_or_404(MeetingFile, id=file_id)
    if request.user != file.uploaded_by:
        messages.error(request, "You are not allowed to delete this file.")
        return redirect('meeting-history-page')
    
    file.delete()
    messages.success(request, "File deleted successfully.")
    return redirect('meeting-history-page')
