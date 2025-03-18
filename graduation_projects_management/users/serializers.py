from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import User, Student

class UserSerializer(serializers.ModelSerializer):
    """
    Handles both user authentication (login) and user creation.
    - Supports Student and Normal User roles.
    """

    password = serializers.CharField(write_only=True)  # Hide password in API response
    role = serializers.ChoiceField(choices=["student", "user"], required=False)  # Optional for user creation
    student_id = serializers.CharField(required=False, allow_blank=True)  # Only needed for Students
    sitting_number = serializers.CharField(required=False, allow_blank=True)  # Only for Students

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "phone_number", "role", "student_id", "sitting_number"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        role = validated_data.pop("role", "user")  # Default to "user"
        student_id = validated_data.pop("student_id", None)
        sitting_number = validated_data.pop("sitting_number", None)

        if role == "student":
            if not student_id or not sitting_number:
                raise serializers.ValidationError({"error": "Student ID and Sitting Number are required for students."})

            user = Student.objects.create_user(**validated_data)
            user.student_id = student_id
            user.sitting_number = sitting_number
            user.save()
            return user

        return User.objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        """
            Updates user, ensuring password hashing and role handling.
        """
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.phone_number = validated_data.get("phone_number", instance.phone_number)

        if validated_data.get("password"):
            instance.set_password(validated_data.get("password"))

        if validated_data.get("department"):
            instance.department = validated_data.get("department")

        instance.save()
        return instance

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        return user
