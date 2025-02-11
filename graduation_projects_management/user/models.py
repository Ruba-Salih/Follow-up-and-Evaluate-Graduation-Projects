from django.db import models
from django.contrib.auth.models import AbstractUser

# Define actor choices
ACTOR_CHOICES = [
    (1, 'Coordinator'),
    (2, 'Supervisor'),
    (3, 'Student'),
    (4, 'Admin'),
    (5, 'Committee Member'),
    (6, 'Reader'),
    (7, 'Dean'),
    (8, 'Teacher'),
]

# Base Member model
class Member(AbstractUser):
    phone_number = models.CharField(max_length=15)
    actor = models.IntegerField(choices=ACTOR_CHOICES)  # Actor number

    class Meta:
        abstract = True

# Child models for users with additional attributes
class Supervisor(Member):
    qualification = models.CharField(max_length=100)
    total_projects = models.IntegerField(default=0)
    supervisor_id = models.CharField(max_length=20, unique=True)
    work_place = models.CharField(max_length=100)

    def __str__(self):
        return f"Supervisor: {self.username}"

class Student(Member):
    student_id = models.CharField(max_length=20, unique=True)
    sitting_number = models.CharField(max_length=20)

    def __str__(self):
        return f"Student: {self.username}"

class Coordinator(Member):
    coord_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Coordinator: {self.username}"

class Admin(Member):
    is_superuser = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    def __str__(self):
        return f"Admin: {self.username}"