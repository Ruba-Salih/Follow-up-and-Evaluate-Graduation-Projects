from django.contrib import admin
from .models import Grade, IndividualGrade, Grading, MemberGrade, MemberIndividualGrade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    # Display key information about the Grade model
    list_display = ("id", "project", "evaluation_form", "grade", "final_grade")
    # Allow searching by grade ID, project ID, and evaluation form ID
    search_fields = ("id", "project__project_id", "evaluation_form__form_id")
    # Filter by evaluation form and project
    list_filter = ("evaluation_form", "project")


@admin.register(IndividualGrade)
class IndividualGradeAdmin(admin.ModelAdmin):
    # Display key information about the IndividualGrade model
    list_display = ("id", "student", "evaluation_form", "grade", "final_grade")
    # Allow searching by individual grade ID, student ID, and evaluation form ID
    search_fields = ("id", "student__student_id", "evaluation_form__form_id")
    # Filter by evaluation form and student
    list_filter = ("evaluation_form", "student")


@admin.register(Grading)
class GradingAdmin(admin.ModelAdmin):
    # Display key information about the Grading model
    list_display = ("id", "final_grade", "student", "project")
    # Allow searching by grading ID and associated grade ID
    search_fields = ("id", "student__student_id", "project__project_id")
    # Filter by grade and project
    list_filter = ("student", "project")


@admin.register(MemberGrade)
class MemberGradeAdmin(admin.ModelAdmin):
    # Display key information about the MemberGrade model
    list_display = ("member", "grade", "grade__id")
    # Allow searching by member username and grade ID
    search_fields = ("member__username", "grade__id")
    # Filter by member and grade
    list_filter = ("member", "grade")


@admin.register(MemberIndividualGrade)
class MemberIndividualGradeAdmin(admin.ModelAdmin):
    # Display key information about the MemberIndividualGrade model
    list_display = ("member", "individual_grade", "individual_grade__id")
    # Allow searching by member username and individual grade ID
    search_fields = ("member__username", "individual_grade__id")
    # Filter by member and individual grade
    list_filter = ("member", "individual_grade")
