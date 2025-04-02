from django.contrib import admin
from .models import EvaluationForm, MainCategory, SubCategory

class SubCategoryInline(admin.TabularInline):
    """Inline admin to allow adding subcategories within MainCategory."""
    model = SubCategory
    extra = 1  # Allows adding extra empty fields for subcategories

class MainCategoryInline(admin.TabularInline):
    """Inline admin to allow adding main categories within EvaluationForm."""
    model = MainCategory
    extra = 1  # Allows adding extra empty fields for main categories
    inlines = [SubCategoryInline]  # Nesting subcategories inside main categories

@admin.register(EvaluationForm)
class EvaluationFormAdmin(admin.ModelAdmin):
    """Admin configuration for EvaluationForm."""
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('coordinators',)  # Better UI for selecting multiple coordinators
    inlines = [MainCategoryInline]  # Allows adding main categories within the form admin

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for MainCategory."""
    list_display = ('id', 'number', 'text', 'weight', 'grade_type', 'evaluation_form')
    list_filter = ('evaluation_form', 'grade_type')
    search_fields = ('text',)
    inlines = [SubCategoryInline]  # Allows adding subcategories within main category admin

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for SubCategory."""
    list_display = ('id', 'text', 'main_category')
    search_fields = ('text',)
    list_filter = ('main_category',)

