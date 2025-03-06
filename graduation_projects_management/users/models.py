from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)

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
    coord_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Coordinator: {self.username}"

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Admin(User):
    #use is_superuser and is_staff flags provided by AbstractUser.
    def __str__(self):
        return f"Admin: {self.username}"
