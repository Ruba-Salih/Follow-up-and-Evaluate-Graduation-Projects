from users.models import User, Student, Coordinator
from django.contrib.auth.hashers import make_password

def create_user_account(username, password, role, created_by, **extra_fields):
    """
    Allows a Coordinator to create new user accounts.
    - Ensures passwords are hashed.
    - Requires `student_id` if role is 'student'.
    - Supports only 'student' and 'user' roles.
    """
    if not isinstance(created_by, Coordinator):
        raise PermissionError("Only Coordinators can create user accounts.")

    if role == "student" and ("student_id" not in extra_fields or "sitting_number" not in extra_fields):
        raise ValueError("student_id and sitting_number are required when creating a Student.")

    hashed_password = make_password(password)

    user = User.objects.create(username=username, password=hashed_password, **extra_fields)

    if role == "student":
        student_id = extra_fields.get("student_id")
        sitting_number = extra_fields.get("sitting_number")
        student = Student.objects.create(
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
            password=user.password,
            department=user.department,
            student_id=student_id,
            sitting_number=sitting_number
        )
        return student

    return user

def is_teacher(user):
    return not any([
        hasattr(user, 'student'),
        hasattr(user, 'coordinator'),
        hasattr(user, 'admin'),
        user.is_superuser,
    ])
