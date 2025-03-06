from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login, logout
from serializers import UserSerializer
from services import create_user_account
from models import Coordinator


class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data

            login(request, user)  

            refresh = RefreshToken.for_user(user)
            return Response({
                "session_id": request.session.session_key,  # Send session ID
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            })
        return Response(serializer.errors, status=400)


class UserLogoutAPIView(APIView):
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

        if not isinstance(user, Coordinator):
            return Response({"error": "Only Coordinators can create user accounts."}, status=403)

        data = request.data
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")
        student_id = data.get("student_id")

        if not username or not password or not role:
            return Response({"error": "All fields are required."}, status=400)
        
        if role == "student" and not student_id:
            return Response({"error": "student_id is required when creating a Student."}, status=400)

        try:
            new_user = create_user_account(username, password, role, created_by=user, student_id=student_id)
            return Response(
                {"message": f"User {new_user.username} created successfully!", "user_id": new_user.id},
                status=201
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)
