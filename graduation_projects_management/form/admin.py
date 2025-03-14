from django.contrib import admin
from .models import EvaluationForm, SubCategory, EditEvaluationForm

@admin.register(EvaluationForm)
class EvaluationFormAdmin(admin.ModelAdmin):
    list_display = ("form_id", "main_category_number", "main_category", "weight", "type_of_grade")
    search_fields = ("main_category", "type_of_grade")
    list_filter = ("type_of_grade",)
    ordering = ("form_id",)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("sub_category_id", "sub_category", "evaluation_form")
    search_fields = ("sub_category",)
    list_filter = ("evaluation_form",)


@admin.register(EditEvaluationForm)
class EditEvaluationFormAdmin(admin.ModelAdmin):
    list_display = ("coordinator", "evaluation_form", "updated_at")
    search_fields = ("coordinator__username", "evaluation_form__form_id")
    list_filter = ("updated_at",)
    ordering = ("-updated_at",)
