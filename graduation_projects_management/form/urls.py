from django.urls import path
from .views import (evaluation_form_list, evaluation_form_detail, create_evaluation_form, edit_evaluation_form, delete_evaluation_form,
delete_main_category, delete_subcategory)


app_name = "form"

urlpatterns = [
    path('', evaluation_form_list, name='form-list'),
    path('', evaluation_form_list, name="evaluation_form_list"),
    path('<int:form_id>/', evaluation_form_detail, name='evaluation_form_detail'),
    path('create/', create_evaluation_form, name='create_evaluation_form'),
    path('<int:form_id>/edit/', edit_evaluation_form, name='edit_evaluation_form'),
    path('delete/<int:form_id>/', delete_evaluation_form, name='delete_evaluation_form'),
    path('main-category/delete/<int:main_category_id>/', delete_main_category, name='delete_main_category'),
    path('subcategory/delete/<int:subcategory_id>/', delete_subcategory, name='delete_subcategory'),
    
]
