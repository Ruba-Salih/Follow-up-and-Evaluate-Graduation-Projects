# reports/serializers.py
from rest_framework import serializers
from .models import ProjectReport, TeamMemberStatus
from users.models import Student

class TeamMemberStatusSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source="student")

    class Meta:
        model = TeamMemberStatus
        fields = ["student_id", "status", "notes"]

class ProjectReportSerializer(serializers.ModelSerializer):
    member_statuses = TeamMemberStatusSerializer(many=True)

    class Meta:
        model = ProjectReport
        fields = [
            "id", "project", "created_by", "report_date",
            "progress", "work_done", "work_remaining", "challenges",
            "member_statuses"
        ]
        read_only_fields = ["created_by"]

    def create(self, validated_data):
        member_data = validated_data.pop("member_statuses")
        report = ProjectReport.objects.create(**validated_data)
        for entry in member_data:
            TeamMemberStatus.objects.create(report=report, **entry)
        return report
