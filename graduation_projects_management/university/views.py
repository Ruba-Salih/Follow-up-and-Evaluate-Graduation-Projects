from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import College, Department
from .serializers import CollegeSerializer, DepartmentSerializer
from django.shortcuts import get_object_or_404

class CollegeView(APIView):
    """
    Handles all College operations: list, create, retrieve, update, delete
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            college = get_object_or_404(College, pk=pk)
            serializer = CollegeSerializer(college)
            return Response(serializer.data)
        colleges = College.objects.all()
        serializer = CollegeSerializer(colleges, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CollegeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        college = get_object_or_404(College, pk=pk)
        serializer = CollegeSerializer(college, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        college = get_object_or_404(College, pk=pk)
        college.delete()
        return Response({"message": "College deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class DepartmentView(APIView):
    """
    Handles all Department operations: list, create, retrieve, update, delete
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            department = get_object_or_404(Department, pk=pk)
            serializer = DepartmentSerializer(department)
            return Response(serializer.data)
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        serializer = DepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        department.delete()
        return Response({"message": "Department deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
