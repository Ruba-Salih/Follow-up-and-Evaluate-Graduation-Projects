from rest_framework import serializers
from .models import University, College, Department

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'college']

class CollegeSerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer(many=True, read_only=True)

    class Meta:
        model = College
        fields = ['id', 'name', 'location', 'university', 'departments']

class UniversitySerializer(serializers.ModelSerializer):
    colleges = CollegeSerializer(many=True, read_only=True)

    class Meta:
        model = University
        fields = ['id', 'name', 'colleges']
