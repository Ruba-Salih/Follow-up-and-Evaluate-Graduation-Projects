# announcement/serializers.py

from rest_framework import serializers
from .models import Announcement
from university.models import Department

class AnnouncementSerializer(serializers.ModelSerializer):
    target_roles = serializers.ListField(
        child=serializers.ChoiceField(choices=Announcement.ROLE_CHOICES),
        help_text="List of roles to send to"
    )
    target_departments = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        many=True,
        required=False,
        help_text="If empty, announcement will target all departments"
    )
    deadline = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Optional deadline after which the announcement becomes inactive"
    )

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'message', 'target_roles',
            'target_departments', 'is_active', 'deadline', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['is_active'] = True  # Always active on creation
        return super().create(validated_data)

