from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Supervisor, Student, Coordinator, Admin, Role, UserCreationLog


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "phone_number", "department", "is_staff", "is_superuser")
    search_fields = ("username", "email", "phone_number")
    list_filter = ("is_staff", "is_superuser", "department")


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ("username", "supervisor_id", "qualification", "work_place", "total_projects")
    search_fields = ("username", "supervisor_id", "work_place")
    list_filter = ("qualification",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("username", "student_id", "sitting_number", "department")
    search_fields = ("username", "student_id", "sitting_number")
    list_filter = ("department",)


@admin.register(Coordinator)
class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ("username", "coord_id", "department")
    search_fields = ("username", "coord_id")
    list_filter = ("department",)


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ("username", "is_staff", "is_superuser")
    search_fields = ("username",)
    list_filter = ("is_staff", "is_superuser")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(UserCreationLog)
class UserCreationLogAdmin(admin.ModelAdmin):
    list_display = ("user", "added_by", "added_at")
    search_fields = ("user__username", "added_by__username")
    list_filter = ("added_at",)
