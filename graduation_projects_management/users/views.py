from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from users.serializers import UserLoginSerializer
from users.services import create_user_account
from users.models import Coordinator
from django.urls import reverse
from project.models import Project
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

            if user.is_staff:
                home_url = "/coordinator/home/"
            elif hasattr(user, "student"):
                home_url = "/student/home/"
            elif hasattr(user, "teacher"):
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


class CreateUserView(APIView):
    """
    Allows a Coordinator to create new user accounts.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Ensure only Coordinators can create accounts
        if not isinstance(user, Coordinator):
            return Response({"error": "Only Coordinators can create user accounts."}, status=403)

        data = request.data
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")
        student_id = data.get("student_id", None)  # Default to None

        # Validate required fields
        if not username or not password or not role:
            return Response({"error": "Username, password, and role are required."}, status=400)
        
        # Ensure student_id is provided when creating a Student
        if role == "student" and not student_id:
            return Response({"error": "student_id is required when creating a Student."}, status=400)

        try:
            extra_fields = {}
            if role == "student":
                extra_fields["student_id"] = student_id

            new_user = create_user_account(username, password, role, created_by=user, **extra_fields)
            return Response(
                {"message": f"User {new_user.username} created successfully!", "user_id": new_user.id},
                status=201
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)
