from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from users.serializers import UserLoginSerializer
from users.services import create_user_account
from users.models import Coordinator


def home_view(request):
    return HttpResponse("<h1>Welcome to the Home Page</h1>")

def login_view(request):
    return render(request, "login.html")


@method_decorator(csrf_exempt, name="dispatch")
class UserLoginAPIView(APIView):
    """
    Handles user login with JWT and session authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data  # Authenticated user object

            login(request, user)  # Log in user (Django session)

            # Ensure session is saved
            request.session.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "session_id": request.session.session_key,  # Send session ID
                "refresh": str(refresh),  # Refresh Token
                "access": str(refresh.access_token),  # Access Token
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }, status=200)
        
        return Response(serializer.errors, status=400)


class UserLogoutAPIView(APIView):
    """
    Logs out the user and clears the session.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)  # Remove session
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
