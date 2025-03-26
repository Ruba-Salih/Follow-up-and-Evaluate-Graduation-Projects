from django.urls import path
from .views import evaluation_form_list, evaluation_form_detail, create_evaluation_form, edit_evaluation_form


app_name = "form"

urlpatterns = [
    path('', evaluation_form_list, name='form-list'),
    path('', evaluation_form_list, name="evaluation_form_list"),
    path('<int:form_id>/', evaluation_form_detail, name='evaluation_form_detail'),
    path('create/', create_evaluation_form, name='create_evaluation_form'),
    path('<int:form_id>/edit/', edit_evaluation_form, name='edit_evaluation_form'),
    
]
