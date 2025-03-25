from django.db import models
from users.models import Coordinator  # Importing Coordinator model

class EvaluationForm(models.Model):
    form_id = models.AutoField(primary_key=True)
    form_name = models.CharField(
        max_length=100,
        help_text="Name of the evaluation form",
        default="Default Form"
    )
    main_category_number = models.IntegerField()
    main_category = models.CharField(max_length=255)
    weight = models.FloatField()  # weight as float
    GRADE_TYPE_CHOICES = [
        ('individual', 'Individual Grade'),
        ('group', 'Group Grade'),
    ]
    type_of_grade = models.CharField(max_length=50, choices=GRADE_TYPE_CHOICES)

    def __str__(self):
        return f"Evaluation Form {self.form_id} - {self.main_category}"


class SubCategory(models.Model):
    sub_category_id = models.AutoField(primary_key=True)
    sub_category = models.CharField(max_length=255)
    evaluation_form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.sub_category


# M:N relationship between the coordinator and the evaluation form
class EditEvaluationForm(models.Model):
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE, related_name="edited_forms")
    evaluation_form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE, related_name="edit_records")
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when edit occurs

    class Meta:
        unique_together = ("coordinator", "evaluation_form")  # Avoid duplicate records

    def __str__(self):
        return f"{self.coordinator.username} edited {self.evaluation_form.form_id} on {self.updated_at}"
