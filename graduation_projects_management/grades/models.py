from django.db import models
from evaluation.models import EvaluationForm
from users.models import Student, User  # Assuming 'users' is the app managing user roles

class Grade(models.Model):
    grade_id = models.CharField(max_length=20, unique=True)
    final_grade = models.FloatField()
    evaluation_form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE, related_name="grades")  # N:1

    def __str__(self):
        return f"Grade {self.grade_id} - {self.final_grade}"


class IndividualGrade(models.Model):
    evaluation_form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE, related_name="individual_grades")  # 1:N
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="individual_grades")  # 1:N
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="individual_grades")  # 1:N
    final_grade = models.FloatField()

    def __str__(self):
        return f"Individual Grade - {self.final_grade}"


class Grading(models.Model):
    grading_id = models.CharField(max_length=20, unique=True)
    final_grade = models.FloatField()
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="gradings")  # 1:N

    def __str__(self):
        return f"Grading {self.grading_id} - Final Grade: {self.final_grade}"


# M:N between Members and Grade (Members include Supervisor, Judging Committee)
class MemberGrade(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="graded_projects")  # M:N
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="members")
    assigned_at = models.DateTimeField(auto_now_add=True)  # Optional tracking field

    def __str__(self):
        return f"{self.member.username} graded {self.grade.grade_id}"


# 1:N between Members and Individual Grade
class MemberIndividualGrade(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="individual_graded_projects")  # 1:N
    individual_grade = models.ForeignKey(IndividualGrade, on_delete=models.CASCADE, related_name="evaluators")
    assigned_at = models.DateTimeField(auto_now_add=True)  # Optional tracking field

    def __str__(self):
        return f"{self.member.username} graded Individual {self.individual_grade.id}"
