from django.db import models
from form.models import EvaluationForm, MainCategory
from users.models import Student, User  # Assuming 'users' is the app managing user roles
from project.models import Project  # Import Project model for the new 1:N relationship

class Grade(models.Model):
    grade = models.FloatField()  # Raw grade before applying weight
    final_grade = models.FloatField()  # Grade after applying weight
    evaluation_form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE, related_name="grades")  # N:1
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="grades")  # 1:N
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name="grades")  # 1:N

    def __str__(self):
        return f"Grade for {self.project} - {self.main_category}"



class IndividualGrade(models.Model):
    evaluation_form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE, related_name="individual_grades")  # 1:N
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="individual_grades")  # 1:N
    final_grade = models.FloatField() # Weighted grade
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="individual_grades")  # 1:N
    #grading = models.ForeignKey("Grading", on_delete=models.CASCADE, related_name="individual_grades", null=True)  # 1:N

    def __str__(self):
        return f"Individual Grade for {self.student} - {self.final_grade}"


class Grading(models.Model):
    final_grade = models.FloatField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="gradings")  # 1:N
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="gradings", null=False, default=1)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Final Grading for {self.student} in {self.project}"


# M:N between Members and Grade (Members include Supervisor, Judging Committee, and Reader)
class MemberGrade(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="graded_projects")  # M:N
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="members")


    class Meta:
        unique_together = ('member', 'grade')  # prevent duplicate grades from same use

    def __str__(self):
        return f"{self.member.username} graded project for {self.grade.project.name}"


# 1:N between Members and Individual Grade
class MemberIndividualGrade(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="individual_graded_projects")  # 1:N
    individual_grade = models.ForeignKey(IndividualGrade, on_delete=models.CASCADE, related_name="evaluators")

    class Meta:
        unique_together = ('member', 'individual_grade')

    def __str__(self):
        return f"{self.member.username} graded {self.individual_grade.student}"
