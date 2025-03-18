from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from users.serializers import UserSerializer, UserLoginSerializer
from users.services import create_user_account
from users.models import User, Student, Supervisor, Coordinator
from university.models import Department
from django.urls import reverse
#from project.models import Project
#from announcement.models import Announcement


def land(request): 
    login_url = reverse("login-page")
    return HttpResponse(f'<a href="{login_url}">Login</a>')


@login_required
def home_redirect_view(request):
    """ Redirect users to their specific home page based on role """
    if request.user.is_staff:
        return redirect("coordinator-home")

    elif hasattr(request.user, "student"):
        return redirect("student-home")

    elif hasattr(request.user, "teacher"):
        return redirect("teacher-home")

@login_required
def coordinator_home(request):
    return render(request, "coordinator/home.html")

@login_required
def student_home(request):
    return render(request, "student/home.html")

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

            if hasattr(user, "coordinator"):
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

    def post(self, request):
        logout(request)
        request.session.flush()
        return Response({"message": "Successfully logged out."}, status=200)


class ManageAccountsView(APIView):
    """
    Allows Coordinators to manage user accounts (Create, Retrieve, Update, Delete).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
         Retrieve all users (both Students & Normal Users)
        """
        users = User.objects.filter(is_staff=False, is_superuser=False)  # ✅ Exclude admin users

        if request.headers.get('Accept') == 'application/json':
            serialized_users = UserSerializer(users, many=True).data
            return Response({"users": serialized_users}, status=200)

        return render(request, "coordinator/manage_accounts.html", {"users": users})

    def post(self, request):
        """
         Create a new user (Student or Normal User)
        """
        user = request.user
        if not isinstance(user, Coordinator):
            return Response({"error": "Only Coordinators can create user accounts."}, status=403)

        data = request.data
        username = data.get("username")
        email = data.get("email", "")
        phone_number = data.get("phone_number", "")
        password = data.get("password")
        role = data.get("role")

        if not username or not password or not role:
            return Response({"error": "Username, password, and role are required."}, status=400)

        department_id = data.get("department_id")
        department = Department.objects.filter(id=department_id).first() if department_id else None

        if role == "student":
            student_id = data.get("student_id")
            sitting_number = data.get("sitting_number")

            if not student_id or not sitting_number:
                return Response({"error": "Student ID and Sitting Number are required for students."}, status=400)

            new_user = Student.objects.create_user(
                username=username, email=email, password=password, phone_number=phone_number, department=department
            )
            new_user.student_id = student_id
            new_user.sitting_number = sitting_number
            new_user.save()

        elif role == "user":
            new_user = User.objects.create_user(
                username=username, email=email, password=password, phone_number=phone_number, department=department
            )

        else:
            return Response({"error": "Invalid role. Choose from 'student' or 'user'."}, status=400)

        return Response({"message": f"User {new_user.username} created successfully!", "user_id": new_user.id}, status=201)

    def put(self, request, user_id):
        """
         Update a user (Only Coordinators can update users)
        """
        user = request.user
        if not isinstance(user, Coordinator):
            return Response({"error": "Only Coordinators can update user accounts."}, status=403)

        data = request.data
        user_obj = get_object_or_404(User, id=user_id)

        user_obj.username = data.get("username", user_obj.username)
        user_obj.email = data.get("email", user_obj.email)
        user_obj.phone_number = data.get("phone_number", user_obj.phone_number)
        if data.get("password"):
            user_obj.set_password(data.get("password"))

        department_id = data.get("department_id")
        if department_id:
            department = Department.objects.filter(id=department_id).first()
            user_obj.department = department

        user_obj.save()
        return Response({"message": f"User {user_obj.username} updated successfully!"}, status=200)

    def delete(self, request, user_id):
        """
         Delete a user (Only Coordinators can delete users)
        """
        user = request.user
        if not isinstance(user, Coordinator):
            return Response({"error": "Only Coordinators can delete user accounts."}, status=403)

        user_obj = get_object_or_404(User, id=user_id)
        user_obj.delete()
        return Response({"message": "User deleted successfully!"}, status=200)