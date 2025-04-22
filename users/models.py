from django.contrib.auth.models import AbstractUser
from django.db import models
from university.models import Department

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
    
        if not self.is_superuser and self.department is None:
            raise ValueError("Non-superusers must have a department.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username



class Supervisor(User):
    qualification = models.CharField(max_length=100)
    total_projects = models.IntegerField(default=0)
    supervisor_id = models.CharField(max_length=20, unique=True)
    work_place = models.CharField(max_length=100)

    def __str__(self):
        return f"Supervisor: {self.username}"


class Student(User):
    student_id = models.CharField(max_length=20, unique=True)
    sitting_number = models.CharField(max_length=20)

    def __str__(self):
        return f"Student: {self.username}"


class Coordinator(User):
    coord_id = models.CharField(max_length=20, unique=True, blank=True, default="")
    is_super = models.BooleanField(default=False)

    def __str__(self):
        return f"Coordinator: {self.username}"


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Admin(User):

    def __str__(self):
        return f"Admin: {self.username}"


class UserCreationLog(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="creation_log")
    added_by = models.ForeignKey(Coordinator, on_delete=models.SET_NULL, null=True, related_name="added_users")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} added by {self.added_by.username if self.added_by else 'Unknown'}"
