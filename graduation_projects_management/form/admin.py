from django.contrib import admin
from .models import EvaluationForm, SubCategory

@admin.register(EvaluationForm)
class EvaluationFormAdmin(admin.ModelAdmin):
    list_display = ('form_id', 'main_category_number', 'main_category', 'weight', 'type_of_grade', 'updated_at')
    list_filter = ('main_category', 'type_of_grade', 'updated_at')
    search_fields = ('main_category', 'type_of_grade')
    ordering = ('-updated_at',)

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('sub_category_id', 'sub_category', 'evaluation_form')
    search_fields = ('sub_category',)
