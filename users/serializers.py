from rest_framework import serializers
from django.contrib.auth import authenticate
from university.models import Department
from users.models import User, Coordinator, Student, Supervisor

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=["student", "user"], required=False)
    student_id = serializers.CharField(required=False, allow_blank=True)
    sitting_number = serializers.CharField(required=False, allow_blank=True)
    coord_id = serializers.CharField(required=False, allow_blank=True)
    department_id = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "password", "phone_number",
            "first_name", "last_name",  
            "role", "student_id", "sitting_number", "coord_id", "department_id"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        role = validated_data.pop("role", "user")
        student_id = validated_data.pop("student_id", None)
        sitting_number = validated_data.pop("sitting_number", None)
        department_id = validated_data.pop("department_id", None)
        coord_id = validated_data.pop("coord_id", None)
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")

        if department_id:
            department = Department.objects.get(id=department_id)
            validated_data["department"] = department

        if role == "student":
            if not student_id or not sitting_number:
                raise serializers.ValidationError({
                    "Error": "Student ID and Sitting Number are required for students."
                })
            user = Student.objects.create_user(**validated_data)
            user.first_name = first_name
            user.last_name = last_name
            user.student_id = student_id
            user.sitting_number = sitting_number
            user.save()
            return user

        if coord_id:
            if Coordinator.objects.filter(coord_id=coord_id).exists():
                raise serializers.ValidationError({"Error": "This Coordinator ID is already in use."})
            user = Coordinator.objects.create_user(
                coord_id=coord_id,
                **validated_data
            )
            user.first_name = first_name
            user.last_name = last_name
            user.is_super = True
            user.save()
            return user

        user = User.objects.create_user(**validated_data)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.phone_number = validated_data.get("phone_number", instance.phone_number)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)


        if validated_data.get("password"):
            instance.set_password(validated_data.get("password"))

        if "department_id" in validated_data:
            department = Department.objects.get(id=validated_data["department_id"])
            instance.department = department

        coord_id = validated_data.get("coord_id")
        if coord_id and hasattr(instance, "coord_id"):
            from users.models import Coordinator
            if Coordinator.objects.exclude(pk=instance.pk).filter(coord_id=coord_id).exists():
                raise serializers.ValidationError({"Error": "This Coordinator ID is already in use."})
            instance.coord_id = coord_id

        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data["username"].lower()  # Normalize to lowercase
        
        # Fetch user case-insensitively from the database
        try:
            user = User.objects.get(username__iexact=username)  # case-insensitive query
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        # Authenticate the user
        user = authenticate(username=user.username, password=data["password"])
        
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
            
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()


class SupervisorProfileSerializer(ProfileSerializer):
    qualification = serializers.CharField()
    work_place = serializers.CharField()

    class Meta(ProfileSerializer.Meta):
        model = Supervisor
        fields = ProfileSerializer.Meta.fields + ['qualification', 'work_place']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'username']

class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = ['id', 'username']
