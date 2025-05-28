from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import College, Department, University
from .serializers import CollegeSerializer, DepartmentSerializer
from django.db.models import Q

class ManageCollegesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_superuser and request.user.is_staff):
            return Response({"error": "Access denied."}, status=403)

        colleges = College.objects.prefetch_related("departments").all()

        if request.headers.get("Accept") == "application/json":
            data = CollegeSerializer(colleges, many=True).data
            return Response({"colleges": data})

        return render(request, "admin/manage_colleges.html", {
            "colleges": colleges
        })

    def post(self, request):
        if not request.headers.get("Content-Type") == "application/json":
            return Response({"error": "Invalid request type."}, status=400)

        if not (request.user.is_superuser and request.user.is_staff):
            return Response({"error": "Only Admins can create colleges."}, status=403)

        name = request.data.get("name")
        departments = request.data.get("departments", [])

        if not name:
            return Response({"error": "College name is required."}, status=400)

        # ✅ Get the default university (first one in the database)
        university = University.objects.first()
        if not university:
            return Response({"error": "No university found. Please create a university first."}, status=400)

        # ✅ Create the college with its university
        college = College.objects.create(name=name, university=university)

        for dept in departments:
            if dept.strip():
                Department.objects.create(name=dept.strip(), college=college)
        return Response({"message": f"College '{college.name}' created successfully!"}, status=201)

    

    def put(self, request, college_id):
        if not (request.user.is_superuser and request.user.is_staff):
            return Response({"error": "Only Admins can update colleges."}, status=403)

        name = request.data.get("name")
        new_departments = request.data.get("departments", [])

        if not name:
            return Response({"error": "College name is required."}, status=400)

        college = get_object_or_404(College, id=college_id)
        college.name = name
        college.save()

        # Get existing department names
        existing_departments = {dept.name: dept for dept in college.departments.all()}

        # Update or create departments
        incoming_names = set()
        for dept_name in new_departments:
            dept_name = dept_name.strip()
            if dept_name:
                incoming_names.add(dept_name)
                if dept_name not in existing_departments:
                    Department.objects.create(name=dept_name, college=college)

        # Delete departments that were removed by admin (and only them)
        to_delete = [dept for name, dept in existing_departments.items() if name not in incoming_names]
        for dept in to_delete:
            dept.delete()  # will cascade to delete users in that department

        return Response({"message": f"College '{college.name}' updated successfully!"})

    def delete(self, request, college_id):
        if not (request.user.is_superuser and request.user.is_staff):
            return Response({"error": "Only Admins can delete colleges."}, status=403)

        college = get_object_or_404(College, id=college_id)
        college.delete()
        return Response({"message": f"College '{college.name}' deleted successfully."}, status=200)


class DepartmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if not (request.user.is_superuser and request.user.is_staff):
            return Response({"error": "Access denied."}, status=403)

        if pk:
            department = get_object_or_404(Department, pk=pk)
            serializer = DepartmentSerializer(department)
            return Response(serializer.data)

        departments = Department.objects.select_related("college").all()
        if request.headers.get("Accept") == "application/json":
            serializer = DepartmentSerializer(departments, many=True)
            return Response(serializer.data)

        return render(request, "admin/manage_departments.html", {
            "departments": departments
        })

    def post(self, request):
        if not (request.user.is_superuser and request.user.is_staff):
            return Response({"error": "Only Admins can create departments."}, status=403)

        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk=None):
        if not (request.user.is_superuser and request.user.is_staff):
            return Response({"error": "Only Admins can update departments."}, status=403)

        department = get_object_or_404(Department, pk=pk)
        serializer = DepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk=None):
        if not (request.user.is_superuser and request.user.is_staff):
            return Response({"error": "Only Admins can delete departments."}, status=403)

        department = get_object_or_404(Department, pk=pk)
        department.delete()
        return Response({"message": "Department deleted successfully."}, status=204)
