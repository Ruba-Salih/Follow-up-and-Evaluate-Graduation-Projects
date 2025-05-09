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
    list_display = ("member", "grade", "get_grade_id")
    search_fields = ("member__username", "grade__id")
    list_filter = ("member", "grade")

    def get_grade_id(self, obj):
        return obj.grade.id
    get_grade_id.short_description = "Grade ID"


@admin.register(MemberIndividualGrade)
class MemberIndividualGradeAdmin(admin.ModelAdmin):
    list_display = ("member", "individual_grade", "get_individual_grade_id")
    search_fields = ("member__username", "individual_grade__id")
    list_filter = ("member", "individual_grade")

    def get_individual_grade_id(self, obj):
        return obj.individual_grade.id
    get_individual_grade_id.short_description = "Individual Grade ID"
