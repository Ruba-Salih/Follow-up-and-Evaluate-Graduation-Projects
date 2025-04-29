from django.shortcuts import render, redirect
from django.shortcuts import  get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import AvailableTime, Meeting, MeetingParticipant
from .serializers import AvailableTimeSerializer, MeetingRequestSerializer, MeetingSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import json
from django.http import HttpResponseNotFound
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from project .models import Project, StudentProjectMembership
from django.views import View
from notifications.models import Notification
from notifications.constants import MEETING_DECLINED, MEETING_ACCEPT, MEETING_REQUEST


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
            created_slots = []
            for item in serializer.validated_data:
                obj, created = AvailableTime.objects.get_or_create(
                    user=request.user,
                    day=item['day'],
                    start_time=item['start_time'],
                    end_time=item['end_time'],
                )
                created_slots.append(obj)
            return Response(AvailableTimeSerializer(created_slots, many=True).data, status=status.HTTP_201_CREATED)
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
        teachers = User.objects.filter(is_staff=True)
        data = [
            {"id": teacher.id, "name": teacher.get_full_name() or teacher.username}
            for teacher in teachers
        ]
        return Response(data)

class TeacherAvailableTimeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, teacher_id):
        available_times = AvailableTime.objects.filter(user_id=teacher_id)
        time_slots = [
            {
                'day': at.day,
                'start_time': at.start_time.strftime('%H:%M'),
                'end_time': at.end_time.strftime('%H:%M')
            }
            for at in available_times
        ]
        return Response(time_slots)
 
class TeacherMeetingRequestsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        meetings = Meeting.objects.filter(requested_by__in=[teacher.id for teacher in request.user.teachers.all()], status='pending')
        serializer = MeetingRequestSerializer(meetings, many=True)
        return Response(serializer.data)


class ScheduleMeetingView(View):
    def get(self, request):
        # Check if the user is a teacher or a student
        if request.user.is_staff:  # Teacher
            # Fetch teacher's college and available projects
            college = request.user.department.college
            projects = Project.objects.filter(department__college=college)

            return render(request, 'meetings/schedule_meeting_teacher.html', {'projects': projects})  # Render teacher-specific template
        elif hasattr(request.user, 'student'):  # Student (assuming the user has a related `student` model)
            return render(request, 'meetings/schedule_meeting_student.html')  # Render student-specific template
        else:
            return render(request, 'home.html')  # For other cases, render a home page


class ScheduleMeetingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        teacher_id = request.data.get('teacher_id')
        day = request.data.get('day')
        meeting_date = request.data.get('meeting_date')
        slot_start_time = request.data.get('slot_start_time')
        slot_end_time = request.data.get('slot_end_time')
        meeting_start_time = request.data.get('meeting_start_time')
        meeting_end_time = request.data.get('meeting_end_time')
        comment = request.data.get('comment')

        short_to_full_day = {
            'sun': 'sunday',
            'mon': 'monday',
            'tue': 'tuesday',
            'wed': 'wednesday',
            'thu': 'thursday',
            'fri': 'friday',
            'sat': 'saturday'
        }


        if not teacher_id or not day or not slot_start_time or not slot_end_time:
            return Response({'error': 'Missing required fields.'}, status=400)
        
        try:
            meeting_date_obj = datetime.strptime(meeting_date, "%Y-%m-%d").date()

            if meeting_start_time and meeting_end_time:
                print(f"meet start at {meeting_start_time} and end at {meeting_end_time}")
                # Validate that the date matches the day
                expected_day = meeting_date_obj.strftime('%A').lower()
                print(f"exected day is {expected_day}")

                if short_to_full_day.get(day.lower(), '') != expected_day:
                    print(f"day is {day.lower()}")
                    return Response({'error': f"The selected date does not match the selected day ({day})."}, status=400)

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


        """ # Handle meeting time: either student format or teacher format
        try:

            if meeting_start_time and meeting_end_time:
                # Student is sending the request
                start_hour, start_minute = map(int, meeting_start_time.split(':'))
                end_hour, end_minute = map(int, meeting_end_time.split(':'))
            else:
                meeting_date = request.data.get('meeting_date')
                print(f"meeting date is: {meeting_date}")
                meeting_date_obj = timezone.make_aware(datetime.strptime(meeting_date, "%Y-%m-%d"))
                # Teacher is sending the request
                start_hour, start_minute = map(int, slot_start_time.split(':'))
                end_hour, end_minute = map(int, slot_end_time.split(':'))
                
                meeting_start = timezone.make_aware(datetime.combine(meeting_date_obj, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute))
                meeting_end = timezone.make_aware(datetime.combine(meeting_date_obj, datetime.min.time()) + timedelta(hours=end_hour, minutes=end_minute))

            
            #meeting_start = timezone.make_aware(datetime(year=2025, month=4, day=10, hour=start_hour, minute=start_minute))
            #meeting_end = timezone.make_aware(datetime(year=2025, month=4, day=10, hour=end_hour, minute=end_minute))
        except ValueError:
            return Response({'error': 'Invalid time format.'}, status=400) """

        # Teacher object
        try:
            teacher = User.objects.get(id=teacher_id)
        except User.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=404)

        # Assign project
        if request.user.is_staff:
            project_id = request.data.get('project_id')
            if not project_id:
                return Response({'error': 'Project field is required for teachers.'}, status=400)

            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return Response({'error': 'Project not found.'}, status=404)
        else:
            try:
                student_membership = StudentProjectMembership.objects.get(student=request.user)
                project = student_membership.project
            except StudentProjectMembership.DoesNotExist:
                return Response({'error': 'Student is not part of any project.'}, status=404)

        # Create meeting
        meeting = Meeting.objects.create(
            requested_by=request.user,
            teacher=teacher, 
            date_time=meeting_start,
            status='pending',
            comment=comment,
            project=project 
        )

        meeting.add_participants()

        # Notifications
        if request.user.is_staff:  # Teacher scheduling the meeting
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


class UpcomingMeetingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_time = timezone.now()
        user = request.user

        # Check if the user is a teacher or a student
        if user.is_staff:
            # User is a teacher, fetch meetings scheduled by the teacher
            upcoming_meetings = Meeting.objects.filter(
                teacher=request.user,  # Assume the user has a 'teacher' relationship
                status='accepted',
                date_time__gte=current_time  # Only future meetings
            ).order_by('date_time')
        else:
            # User is a student, fetch meetings related to the student's projects
            student_memberships = StudentProjectMembership.objects.filter(student=request.user)
            project_ids = [membership.project.id for membership in student_memberships]

            upcoming_meetings = Meeting.objects.filter(
                project__id__in=project_ids,  # Filter meetings for projects the student is part of
                status='accepted',
                date_time__gte=current_time  # Only future meetings
            ).order_by('date_time')

        for meeting in upcoming_meetings:
            print(meeting.teacher)  # Check if teacher is populated
            print(meeting.project)
        # Serialize the meetings to return in the response
        serializer = MeetingSerializer(upcoming_meetings, many=True)
        return Response(serializer.data)

# ------------------- PAGE VIEWS -------------------

@login_required
def set_available_time_page(request):
    day_choices = AvailableTime.DAYS_OF_WEEK
    return render(request, 'meetings/set_available_time.html', {'day_choices': day_choices})

@login_required
def meeting_requests_page(request):
    if request.user.is_staff:  # Teacher
        # Fetch all pending meetings where the teacher is the recipient
        meetings = Meeting.objects.filter(teacher=request.user, status='pending').exclude(requested_by=request.user)
    else:  # Student
        # Fetch all pending meetings related to the student's project
        try:
            student_membership = StudentProjectMembership.objects.get(student=request.user)
            meetings = Meeting.objects.filter(project=student_membership.project, status='pending').exclude(requested_by=request.user)
        except StudentProjectMembership.DoesNotExist:
            # If the student is not part of any project, return an empty list
            meetings = []

    # Pass the meetings to the template
    return render(request, 'meetings/meeting_requests.html', {'meetings': meetings})


@login_required
def meeting_history_page(request):
    if request.user.is_staff:  # Teacher
        # Fetch all meetings where the teacher is the requester and the status is 'pending' or 'completed'
        meetings = Meeting.objects.filter(requested_by=request.user, status__in=['canceled', 'completed', 'accepted'])
    else:  # Student
        # Fetch all meetings where the student is a member of the project, status is 'pending' or 'completed', and exclude their own requests
        try:
            student_membership = StudentProjectMembership.objects.get(student=request.user)
            meetings = Meeting.objects.filter(project=student_membership.project, status__in=['canceled', 'completed']).exclude(requested_by=request.user)
        except StudentProjectMembership.DoesNotExist:
            # If the student is not part of any project, return an empty list
            meetings = []

    # Pass the meetings and attendance status for each participant to the template
    meeting_participants = {}
    for meeting in meetings:
        participants = MeetingParticipant.objects.filter(meeting=meeting)
        meeting_participants[meeting.meeting_id] = participants
    
    # Render the template with the meeting details and participant attendance information
    return render(request, 'meetings/meeting_history.html', {
        'meetings': meetings,
        'meeting_participants': meeting_participants
    })



@login_required
def accept_meeting(request, meeting_id):
    try:
        meeting = Meeting.objects.get(meeting_id=meeting_id)
    except Meeting.DoesNotExist:
        return HttpResponseNotFound("Meeting not found")
    
    user = request.user

    # Accept the meeting
    meeting.status = 'accepted'
    meeting.save()

    # Send notifications
    if user.is_staff:
        # If the user is a teacher, notify students in the project
        students = meeting.project.student_memberships.all()
        for membership in students:
            Notification.objects.create(
                recipient=membership.student,
                message=f"Your meeting request has been accepted by {user.get_full_name()}.",
                notification_type=MEETING_ACCEPT
            )
    else:
        # If the user is a student, notify the teacher and other group members
        # Notify the teacher
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
    if user.is_staff:
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

    # Only allow teachers (staff) to update the meeting
    if not request.user.is_staff:
        messages.error(request, "You are not authorized to update this meeting.")
        return redirect('meeting-history')

    if request.method == 'POST':
        # Update the status of the meeting
        status = request.POST.get('status')
        meeting.status = status
        meeting.save()

        # Update attendance for each participant
        for participant in meeting.participants.all():
            attended = request.POST.get(f'attendance_{participant.id}')
            if attended:
                participant.attendance_status = 'attended'
            else:
                participant.attendance_status = 'absent'
            participant.save()

        messages.success(request, "Meeting status and attendance have been updated.")
        return redirect('meeting-history-page')  # Redirect back to meeting history page

    return render(request, 'meetings/meeting_requests.html', {'meeting': meeting})