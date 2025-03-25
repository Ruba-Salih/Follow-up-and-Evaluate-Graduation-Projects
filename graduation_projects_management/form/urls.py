from django.urls import path
from .views import EvaluationFormListCreateView, EvaluationFormCreateView, EvaluationFormDetailView

urlpatterns = [
    path('evaluation-forms/', EvaluationFormListCreateView.as_view(), name='evaluation_form_list_create'),
    path('evaluation-forms/create/', EvaluationFormCreateView.as_view(), name='evaluation_form_create'),
    path('evaluation-forms/<int:pk>/', EvaluationFormDetailView.as_view(), name='evaluation_form_detail'),
]
