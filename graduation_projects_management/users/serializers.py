from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Handles both user authentication (login) and user creation.
    """

    password = serializers.CharField(write_only=True)  # Hide password in API response
    role = serializers.ChoiceField(choices=["student", "coordinator"], required=False)  # Optional for user creation
    student_id = serializers.CharField(required=False, allow_blank=True)  # Required for student creation

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "student_id"]


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        return user
