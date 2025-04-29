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



User = get_user_model()

class MeetingRequestSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )
    date_time = serializers.DateTimeField()  # The datetime of the meeting, which the student chooses

    class Meta:
        model = Meeting
        fields = ['meeting_id', 'date_time', 'status', 'recommendation', 'participants']

    def validate(self, attrs):
        date_time = attrs.get('date_time')
        participants = self.initial_data.get('participants', [])

        if not participants:
            raise ValidationError("You must select a teacher.")

        teacher_id = participants[0]
        available_times = AvailableTime.objects.filter(user_id=teacher_id)

        valid_slot = False
        for slot in available_times:
            if slot.start_time <= date_time.time() <= slot.end_time:
                valid_slot = True
                break

        if not valid_slot:
            raise ValidationError("The selected teacher is not available at the chosen time.")

        return attrs


    def create(self, validated_data):
        participants = validated_data.pop('participants')
        meeting = Meeting.objects.create(**validated_data)
        for user in participants:
            MeetingParticipant.objects.create(meeting=meeting, user=user)
        return meeting

class MeetingParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingParticipant
        fields = ['user', 'attendance_status']
        read_only_fields = ['attendance_status']



class MeetingSerializer(serializers.ModelSerializer):
    project = serializers.CharField(source='project.name', read_only=True)
    teacher = serializers.SerializerMethodField()
    date_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Meeting
        fields = ['meeting_id', 'requested_by', 'teacher', 'project', 'status', 'date_time', 'recommendation', 'comment']

    def get_teacher(self, obj):
        if obj.teacher:
            full_name = obj.teacher.get_full_name()
            if full_name.strip():  # if full name is not empty
                return full_name
            return obj.teacher.username  # fallback to username
        return ''

