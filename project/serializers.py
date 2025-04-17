from rest_framework import serializers
from users.serializers import StudentSerializer

from .models import (
    ProjectProposal, Project, ProjectPlan, ProjectMembership,
    StudentProjectMembership, AnnualGrade, FeedbackExchange
)
from users.models import Student, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class ProjectProposalSerializer(serializers.ModelSerializer):

    team_members = StudentSerializer(many=True, read_only=True)

    team_members_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Student.objects.all(),
        source='team_members'
    )

    class Meta:
        model = ProjectProposal
        fields = '__all__'
        read_only_fields = ['submitted_by', 'created_at', 'updated_at']

    def validate_team_member_count(self, value):
        if value == "" or value is None:
            return 0
        return value

    def create(self, validated_data):
        team_members = validated_data.pop('team_members', [])
        proposal = ProjectProposal.objects.create(**validated_data)
        proposal.team_members.set(team_members)
        return proposal

    def update(self, instance, validated_data):
        team_members = validated_data.pop('team_members', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if team_members is not None:
            instance.team_members.set(team_members)
        return instance


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPlan
        fields = '__all__'


class ProjectMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembership
        fields = '__all__'


class StudentProjectMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProjectMembership
        fields = '__all__'


class AnnualGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnualGrade
        fields = '__all__'


class FeedbackExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackExchange
        fields = '__all__'
