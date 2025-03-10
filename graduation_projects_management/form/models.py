from django.db import models

class EvaluationForm(models.Model):
    form_id = models.AutoField(primary_key=True)
    main_category_number = models.IntegerField()
    main_category = models.CharField(max_length=255)
    weight = models.FloatField()
    type_of_grade = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Evaluation Form {self.form_id} - {self.title}"

class SubCategory(models.Model):
    sub_category_id = models.AutoField(primary_key=True)
    sub_category = models.CharField(max_length=255)
    evaluation_form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.sub_category
