# serializers.py
from rest_framework import serializers
from .models import Meeting, MeetingParticipant
from django.contrib.auth import get_user_model
from .models import AvailableTime
from rest_framework.exceptions import ValidationError


class AvailableTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTime
        fields = ['day', 'start_time', 'end_time']
        extra_kwargs = {
            'user': {'read_only': True},  # Ensure 'user' is read-only and not expected in the request
        }


User = get_user_model()

class MeetingRequestSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )

    # Removed 'date_time' field because we are using start_datetime and end_datetime
    start_datetime = serializers.DateTimeField()  # The start datetime of the meeting
    end_datetime = serializers.DateTimeField()    # The end datetime of the meeting

    class Meta:
        model = Meeting
        fields = ['meeting_id', 'start_datetime', 'end_datetime', 'status', 'recommendation', 'participants']

    def validate(self, attrs):
        start_datetime = attrs.get('start_datetime')
        end_datetime = attrs.get('end_datetime')
        participants = self.initial_data.get('participants', [])

        if not participants:
            raise ValidationError("You must select a teacher.")

        teacher_id = participants[0]
        
        # Check if the teacher is available at the selected time
        available_times = AvailableTime.objects.filter(user_id=teacher_id)
        valid_slot = False
        for slot in available_times:
            if slot.start_time <= start_datetime.time() <= slot.end_time:
                valid_slot = True
                break

        if not valid_slot:
            raise ValidationError("The selected teacher is not available at the chosen time.")

        # Check if the student already has a meeting at the selected time
        student_id = self.context['request'].user.id  # Assuming the student is logged in
        conflicting_meeting = Meeting.objects.filter(
            start_datetime__lte=end_datetime,
            end_datetime__gte=start_datetime,
            participants__id=student_id
        ).exists()

        if conflicting_meeting:
            raise ValidationError("You already have a meeting at this time.")

        # Check if the time slot is already taken by another student for this teacher
        conflicting_teacher_meeting = Meeting.objects.filter(
            start_datetime__lte=end_datetime,
            end_datetime__gte=start_datetime,
            teacher_id=teacher_id
        ).exists()

        if conflicting_teacher_meeting:
            raise ValidationError("This time slot is already taken by another student.")

        return attrs
    


class MeetingParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingParticipant
        fields = ['user', 'attendance_status']
        read_only_fields = ['attendance_status']



class MeetingSerializer(serializers.ModelSerializer):
    start_datetime_display = serializers.SerializerMethodField()
    end_datetime_display = serializers.SerializerMethodField()
    project = serializers.CharField(source='project.name', read_only=True)
    teacher = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = ['meeting_id', 'requested_by', 'teacher', 'project', 'status', 'start_datetime', 'end_datetime', 'start_datetime_display',
            'end_datetime_display', 'recommendation', 'comment']

    def get_teacher(self, obj):
        if obj.teacher:
            full_name = obj.teacher.get_full_name()
            if full_name.strip():  # if full name is not empty
                return full_name
            return obj.teacher.username  # fallback to username
        return ''

    def get_start_datetime_display(self, obj):
        return obj.start_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
        # e.g., "Monday, May 27, 2025 at 02:30 PM"

    def get_end_datetime_display(self, obj):
        return obj.end_datetime.strftime("%I:%M %p")
