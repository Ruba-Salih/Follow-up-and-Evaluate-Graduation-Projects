from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from users.serializers import UserSerializer, UserLoginSerializer, ProfileSerializer, PasswordChangeSerializer, SupervisorProfileSerializer
from users.services import create_user_account
from users.models import User, Student, Supervisor, Coordinator
from university.models import College, Department
from django.urls import reverse
from grades.models import Grading
#from project.models import Project
#from announcement.models import Announcement


def land(request): 
    #login_url = reverse("login-page")
    return render(request, "landing.html")


@login_required
def home_redirect_view(request):
    """ Redirect users to their specific home page based on role """
    user = request.user

    if user.is_authenticated and user.is_superuser and user.is_staff:
        return redirect("admin-home")
    elif user.is_staff:
        return redirect("coordinator-home")
    elif hasattr(user, "student"):
        return redirect("student-home")
    elif hasattr(user, "teacher"):
        return redirect("teacher-home")

    return redirect("login")

def is_admin(user):
    return user.is_authenticated and user.is_superuser and user.is_staff

@user_passes_test(is_admin)
def admin_home(request):
    colleges = College.objects.all()
    departments = Department.objects.all()
    super_coords = Coordinator.objects.filter(is_super=True)

    return render(request, "admin/home.html", {
        "colleges": colleges,
        "departments": departments,
        "super_coords": super_coords,
    })

@login_required
def coordinator_home(request):
    return render(request, "coordinator/home.html")

@login_required
def student_home(request):
    student = request.user.student
    grading = Grading.objects.filter(student=student).first()

    return render(request, 'student/home.html', {
        'grading': grading,
    })

@login_required
def teacher_home(request):
    #total_projects = Project.objects.filter(teacher=request.user).count()
    #announcements = Announcement.objects.all().order_by('-date_posted')[:5]

    #return render(request, "teacher/home.html", {
        #"total_projects": total_projects,
        #"announcements": announcements,
    #})

    return render(request, "teacher/home.html")

def login_view(request):
    return render(request, "login.html")

@login_required
def coordinator_dashboard(request):
    return render(request, "coordinator/dashboard.html")


@method_decorator(csrf_exempt, name="dispatch")
class UserLoginAPIView(APIView):
    """
    Handles user login with JWT and session authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data

            login(request, user)
            request.session.save()

            if  user.is_superuser and user.is_staff:
                home_url = "/admin-home/home/"
            elif hasattr(user, "coordinator"):
                home_url = "/coordinator/home/"
            elif hasattr(user, "student"):
                home_url = "/student/home/"
            else:
                home_url = "/teacher/home/"

            refresh = RefreshToken.for_user(user)
            return Response({
                "session_id": request.session.session_key,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "home_url": home_url
                }
            }, status=200)
        print("Login Error:", serializer.errors)
        return Response({"error": "Invalid credentials."}, status=400)

    def get(self, request):
        return JsonResponse({"error": "GET method not allowed."}, status=405)


class UserLogoutAPIView(APIView):
    """
    Logs out the user and clears the session.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        request.session.flush()
        return redirect("land")

    def post(self, request):
        logout(request)
        request.session.flush()
        return redirect("land")

@user_passes_test(is_admin)
def manage_super_coordinators(request):
    return render(request, 'admin/manage_super_coords.html')


class SuperCoordinatorView(APIView):
    """
    Manage Super Coordinators (Admin Only) with both HTML and JSON responses.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Access denied"}, status=403)

        coords = Coordinator.objects.filter(is_super=True)

        if request.headers.get("Accept") == "application/json":
            return Response(UserSerializer(coords, many=True).data)

        departments = Department.objects.select_related("college").all()

        return render(request, "admin/manage_super_coords.html", {
            "super_coords": coords,
            "departments": departments
        })

    def post(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Access denied"}, status=403)

        mutable_data = request.data.copy()
        mutable_data["is_super"] = True

        department_id = mutable_data.get("department_id")
        if not department_id:
            return Response({"error": "Department is required."}, status=400)

        mutable_data["is_super"] = True 

        serializer = UserSerializer(data=mutable_data)

        if serializer.is_valid():
            user = serializer.save()
            user.is_staff = True
            user.set_password(mutable_data["password"])
            user.save()

            if hasattr(user, "coordinator"):
                user.coordinator.is_super = True
                user.coordinator.coord_id = f"C-{user.pk}"
                user.coordinator.save()

            return Response(UserSerializer(user).data, status=201)

        return Response(serializer.errors or {"error": "Invalid data"}, status=400)

    def put(self, request, pk=None):
        if not request.user.is_superuser:
            return Response({"error": "Access denied"}, status=403)

        coord = get_object_or_404(Coordinator, pk=pk, is_super=True)
        serializer = UserSerializer(coord, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk=None):
        if not request.user.is_superuser:
            return Response({"error": "Access denied"}, status=403)

        coord = get_object_or_404(Coordinator, pk=pk, is_super=True)
        coord.delete()
        return Response({"message": "Super Coordinator deleted."}, status=204)    


class ManageAccountsView(APIView):
    """
    Allows Admins and Coordinators to manage user accounts.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_superuser and user.is_staff:
            users = User.objects.filter(is_superuser=False)
            departments = Department.objects.all()

        elif hasattr(user, "coordinator") and user.coordinator.is_super:
            college_departments = Department.objects.filter(college=user.department.college)
            users = User.objects.filter(
                is_superuser=False,
                department__in=college_departments
            ).exclude(coordinator__is_super=True)
            departments = college_departments

        elif hasattr(user, "coordinator"):
            users = User.objects.filter(
                is_superuser=False,
                department=user.department
            ).exclude(id__in=Coordinator.objects.values_list("id", flat=True))
            departments = [user.department]

        else:
            return Response({"error": "Access denied."}, status=403)

        if request.headers.get("Accept") == "application/json":
            serialized_users = UserSerializer(users, many=True).data
            return Response({
                "users": serialized_users,
                "departments": [{"id": dept.id, "name": dept.name} for dept in departments],
                "is_super": (hasattr(user, "coordinator") and user.coordinator.is_super) or user.is_superuser
            })

        return render(request, "coordinator/manage_accounts.html", {
            "users": users,
            "departments": departments,
            "is_super": (hasattr(user, "coordinator") and user.coordinator.is_super) or user.is_superuser
        })

    def post(self, request):
        """
        Create a new user (Student, Teacher, or Coordinator)
        """
        user = request.user
        is_admin = user.is_superuser and user.is_staff

        data = request.data
        username = data.get("username")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        email = data.get("email", "")
        phone_number = data.get("phone_number", "")
        password = data.get("password")
        role = data.get("role")

        if not username or not password or not role:
            return Response({"error": "Username, password, and role are required."}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=400)

        department_id = data.get("department_id")
        department = None

        if is_admin:
            department = Department.objects.filter(id=department_id).first()
        elif hasattr(user, "coordinator") and user.coordinator.is_super:
            department = Department.objects.filter(id=department_id, college=user.department.college).first()
        elif hasattr(user, "coordinator"):
            department = user.department
        else:
            return Response({"error": "Permission denied."}, status=403)

        if role == "coordinator":
            coord_id = data.get("coord_id")
            is_super = data.get("is_super", False)
            
            # Step 1: Create user with temporary coord_id value
            new_user = Coordinator.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                phone_number=phone_number,
                department=department,
                coord_id="",  # Placeholder
                is_super=is_super
            )

            # Step 2: Generate and set coord_id using the primary key
            new_user.coord_id = f"C-{new_user.pk}"
            new_user.save()

            """ # Step 1: Create the Coordinator object
            new_user = Coordinator(
                username=username,
                email=email,
                password=password,
                phone_number=phone_number,
                department=department,
                is_super=is_super
            )

            # Step 2: Assign coord_id before saving
            new_user.coord_id = f"C-{new_user.pk if new_user.pk else 0:04d}"

            # Step 3: Save the object
            new_user.save()
            is_super = data.get("is_super", False) """

        elif role == "student":
            student_id = data.get("student_id")
            sitting_number = data.get("sitting_number")

            if not student_id or not sitting_number:
                return Response({"error": "Student ID and Sitting Number are required."}, status=400)

            if Student.objects.filter(student_id=student_id).exists():
                return Response({"error": "Student ID already exists."}, status=400)

            if Student.objects.filter(sitting_number=sitting_number).exists():
                return Response({"error": "Sitting number already exists."}, status=400)

            new_user = Student.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                phone_number=phone_number,
                department=department,
                student_id=student_id,
                sitting_number=sitting_number
            )

        elif role == "user":
            new_user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                phone_number=phone_number,
                department=department
            )

        else:
            return Response({"error": "Invalid role."}, status=400)

        return Response({"message": f"{role.capitalize()} '{new_user.username}' created successfully!"}, status=201)

    def put(self, request, user_id):
        """
        Update a user
        """
        user = request.user
        target = get_object_or_404(User, id=user_id)
        data = request.data

        if not (user.is_superuser or hasattr(user, "coordinator")):
            return Response({"error": "Unauthorized"}, status=403)

        target.username = data.get("username", target.username)
        target.first_name = data.get("first_name", target.first_name)
        target.last_name = data.get("last_name", target.last_name)
        target.email = data.get("email", target.email)
        target.phone_number = data.get("phone_number", target.phone_number)
        if data.get("password"):
            target.set_password(data["password"])

        department_id = data.get("department_id")
        if department_id:
            department = Department.objects.filter(id=department_id).first()
            if department:
                target.department = department

        target.save()
        return Response({"message": f"User '{target.username}' updated successfully!"}, status=200)

    def delete(self, request, user_id):
        """
        Delete a user
        """
        user = request.user
        if not (user.is_superuser or hasattr(user, "coordinator")):
            return Response({"error": "Unauthorized"}, status=403)

        target = get_object_or_404(User, id=user_id)
        target.delete()
        return Response({"message": f"User '{target.username}' deleted."}, status=200)


@login_required
def profile_page(request):
    user = request.user

    if hasattr(user, 'admin'):
        return render(request, 'admin/profile.html')
    elif hasattr(user, 'student'):
        return render(request, 'student/profile.html')
    elif hasattr(user, 'coordinator'):
        return render(request, 'coordinator/profile.html')
    else:
        return render(request, 'teacher/profile.html')


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self, user):
        if hasattr(user, 'supervisor'):
            return SupervisorProfileSerializer
        return ProfileSerializer

    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        data = serializer.data

        if Supervisor.objects.filter(pk=user.pk).exists():
            supervisor = Supervisor.objects.get(pk=user.pk)
            data['qualification'] = supervisor.qualification
            data['work_place'] = supervisor.work_place

        return Response(data)

    def put(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            if Supervisor.objects.filter(pk=user.pk).exists():
                supervisor = Supervisor.objects.get(pk=user.pk)
                supervisor.qualification = request.data.get('qualification', supervisor.qualification)
                supervisor.work_place = request.data.get('work_place', supervisor.work_place)
                supervisor.save()

            return Response({"message": "Profile updated"})
        return Response(serializer.errors, status=400)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"error": "Incorrect old password"}, status=400)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password updated"})
        return Response(serializer.errors, status=400)
