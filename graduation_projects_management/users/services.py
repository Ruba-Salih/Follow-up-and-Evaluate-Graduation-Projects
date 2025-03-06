from users.models import User, Student, Coordinator
from django.contrib.auth.hashers import make_password

def create_user_account(username, password, role, created_by, **extra_fields):
    """
    Allows a Coordinator to create new user accounts.
    - Ensures passwords are hashed.
    - Requires `student_id` if role is 'student'.
    - Supports 'student' and 'coordinator' roles.
    """
    if not isinstance(created_by, Coordinator):
        raise PermissionError("Only Coordinators can create user accounts.")

    # Ensure student_id is provided if role is 'student'
    if role == "student" and "student_id" not in extra_fields:
        raise ValueError("student_id is required when creating a Student.")

    # Hash the password before saving
    hashed_password = make_password(password)

    # Create the user
    user = User.objects.create(username=username, password=hashed_password, **extra_fields)

    if role == "student":
        Student.objects.create(user=user, student_id=extra_fields["student_id"])

    elif role == "coordinator":
        Coordinator.objects.create(user=user, is_coordinator=True)

    return user
