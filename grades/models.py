from django.db import models
from django.utils.translation import gettext_lazy as _
from form.models import EvaluationForm, MainCategory
from users.models import Student, User
from project.models import Project


class Grade(models.Model):
    grade = models.FloatField(_("Raw Grade"))  # Raw grade before applying weight
    final_grade = models.FloatField(_("Final Grade"))  # Grade after applying weight
    evaluation_form = models.ForeignKey(
        EvaluationForm,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name=_("Evaluation Form")
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name=_("Project")
    )
    main_category = models.ForeignKey(
        MainCategory,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name=_("Main Category")
    )

    def __str__(self):
        return f"{_('Grade for')} {self.project} - {self.main_category}"


class IndividualGrade(models.Model):
    evaluation_form = models.ForeignKey(
        EvaluationForm,
        on_delete=models.CASCADE,
        related_name="individual_grades",
        verbose_name=_("Evaluation Form")
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="individual_grades",
        verbose_name=_("Overall Grade")
    )
    final_grade = models.FloatField(_("Final Individual Grade"))
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="individual_grades",
        verbose_name=_("Student")
    )

    def __str__(self):
        return f"{_('Individual Grade for')} {self.student} - {self.final_grade}"


class Grading(models.Model):
    final_grade = models.FloatField(_("Final Grade"))
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="gradings",
        verbose_name=_("Student")
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="gradings",
        null=False,
        default=1,
        verbose_name=_("Project")
    )
    is_sent = models.BooleanField(_("Is Sent"), default=False)

    def __str__(self):
        return f"{_('Final Grading for')} {self.student} {_('in')} {self.project}"


class MemberGrade(models.Model):
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="graded_projects",
        verbose_name=_("Member")
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name=_("Grade")
    )

    class Meta:
        unique_together = ('member', 'grade')
        verbose_name = _("Member Grade")
        verbose_name_plural = _("Member Grades")

    def __str__(self):
        return f"{self.member.username} {_('graded project for')} {self.grade.project.name}"


class MemberIndividualGrade(models.Model):
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="individual_graded_projects",
        verbose_name=_("Member")
    )
    individual_grade = models.ForeignKey(
        IndividualGrade,
        on_delete=models.CASCADE,
        related_name="evaluators",
        verbose_name=_("Individual Grade")
    )

    class Meta:
        unique_together = ('member', 'individual_grade')
        verbose_name = _("Member Individual Grade")
        verbose_name_plural = _("Member Individual Grades")

    def __str__(self):
        return f"{self.member.username} {_('graded')} {self.individual_grade.student}"
