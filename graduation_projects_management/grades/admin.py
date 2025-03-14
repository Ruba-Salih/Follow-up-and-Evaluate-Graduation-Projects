from django.contrib import admin
from .models import Grade, IndividualGrade, Grading, MemberGrade, MemberIndividualGrade

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("grade_id", "project", "evaluation_form", "grade", "final_grade")
    search_fields = ("grade_id", "project__project_id", "evaluation_form__form_id")
    list_filter = ("evaluation_form", "project")


@admin.register(IndividualGrade)
class IndividualGradeAdmin(admin.ModelAdmin):
    list_display = ("in_grade_id", "student", "evaluation_form", "grade", "final_grade")
    search_fields = ("in_grade_id", "student__student_id", "evaluation_form__form_id")
    list_filter = ("evaluation_form", "student")


@admin.register(Grading)
class GradingAdmin(admin.ModelAdmin):
    list_display = ("grading_id", "grade", "final_grade")
    search_fields = ("grading_id", "grade__grade_id")
    list_filter = ("grade",)


@admin.register(MemberGrade)
class MemberGradeAdmin(admin.ModelAdmin):
    list_display = ("member", "grade")
    search_fields = ("member__username", "grade__grade_id")
    list_filter = ("member", "grade")


@admin.register(MemberIndividualGrade)
class MemberIndividualGradeAdmin(admin.ModelAdmin):
    list_display = ("member", "individual_grade")
    search_fields = ("member__username", "individual_grade__in_grade_id")
    list_filter = ("member", "individual_grade")
