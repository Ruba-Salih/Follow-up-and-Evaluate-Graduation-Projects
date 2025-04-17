from django.db import models
# Import Coordinator from your users app
from users.models import Coordinator  
# Import Role from your project app (adjust the path as needed)
from project.models import Role  
from django.utils.timezone import now

class EvaluationForm(models.Model):
    """
    Represents an Evaluation Form.
    - Coordinators (via a ManyToManyField) are allowed to create and edit forms.
    - target_role associates the form with a specific user role (from your Role model).
    """
    name = models.CharField(max_length=255)
    coordinators = models.ManyToManyField(Coordinator, blank=True, related_name='evaluation_forms')
    target_role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="The role of users for whom this evaluation form is intended."
    )
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Form {self.id}: {self.name}"


class MainCategory(models.Model):
    """
    A main category belongs to a specific EvaluationForm.
    - number: an integer representing the order or label.
    - text: the main category description.
    - weight: a float representing the category’s weight.
    - grade_type: a choice field for 'individual' or 'group' grading.
    """
    GRADE_TYPE_CHOICES = (
        ('individual', 'Individual Grade'),
        ('group', 'Group Grade'),
    )

    evaluation_form = models.ForeignKey(
        EvaluationForm, 
        on_delete=models.CASCADE, 
        related_name='main_categories'
    )
    number = models.PositiveIntegerField()
    text = models.TextField()
    weight = models.FloatField()
    grade_type = models.CharField(max_length=20, choices=GRADE_TYPE_CHOICES)

    def __str__(self):
        return f"Main Category {self.number} (Form {self.evaluation_form.id})"


class SubCategory(models.Model):
    """
    A subcategory belongs to a specific MainCategory.
    Only the text is stored.
    """
    main_category = models.ForeignKey(
        MainCategory, 
        on_delete=models.CASCADE, 
        related_name='sub_categories'
    )
    text = models.TextField()

    def __str__(self):
        return f"SubCategory for MainCategory {self.main_category.number}"
