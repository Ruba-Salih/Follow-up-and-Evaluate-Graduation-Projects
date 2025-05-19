from rest_framework import serializers
from datetime import datetime
from users.serializers import StudentSerializer
from .models import (
    ProjectProposal, Project, ProjectPlan, ProjectMembership,
    ProjectGoal, ProjectTask, StudentProjectMembership, AnnualGrade,
    FeedbackExchange
)
from users.models import Supervisor, Student, Role
from university.models import Department
from university.serializers import DepartmentSerializer
from .services import assign_project_memberships


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

def get_academic_year():
    now = datetime.now()
    return f"{now.year}-{now.year + 1}" if now.month >= 8 else f"{now.year - 1}-{now.year}"


class MembershipReadSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    role = serializers.CharField(source='role.name')

    class Meta:
        model = ProjectMembership
        fields = ['user_id', 'username', 'role', 'group_id']


class ProjectSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True
    )

    supervisor_id = serializers.PrimaryKeyRelatedField(
        queryset=Supervisor.objects.all(),
        source='supervisor',
        write_only=True,
        required=False
    )
    supervisor = serializers.StringRelatedField(read_only=True)

    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    assigned_students = serializers.SerializerMethodField()


    memberships = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    members = MembershipReadSerializer(source='projectmembership_set', many=True, read_only=True)
    research_file = serializers.FileField(required=False, allow_null=True)


    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['academic_year']

    def get_assigned_students(self, obj):
        return list(
            obj.student_memberships.values_list("student_id", flat=True)
        )
    def create(self, validated_data):
        student_ids = validated_data.pop('student_ids', [])
        memberships = validated_data.pop('memberships', [])

        validated_data.setdefault("academic_year", get_academic_year())
        project = Project.objects.create(**validated_data)

        for sid in student_ids:
            Student.objects.filter(id=sid).exists() and StudentProjectMembership.objects.create(student_id=sid, project=project)

        assign_project_memberships(project, memberships)

        return project

    def update(self, instance, validated_data):
        student_ids = validated_data.pop('student_ids', None)
        memberships = validated_data.pop('memberships', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if student_ids is not None:
            StudentProjectMembership.objects.filter(project=instance).delete()
            for sid in student_ids:
                Student.objects.filter(id=sid).exists() and StudentProjectMembership.objects.create(student_id=sid, project=instance)

        if memberships is not None:
            ProjectMembership.objects.filter(project=instance).delete()
            assign_project_memberships(instance, memberships)

        return instance


class ProjectGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectGoal
        fields = '__all__'


class ProjectTaskSerializer(serializers.ModelSerializer):
    assign_to = StudentSerializer(read_only=True)

    class Meta:
        model = ProjectTask
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
