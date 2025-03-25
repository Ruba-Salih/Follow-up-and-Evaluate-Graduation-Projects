from django.urls import path
from . import views

urlpatterns = [
    path('colleges/', views.CollegeView.as_view(), name='college-list-create'),
    path('colleges/<int:pk>/', views.CollegeView.as_view(), name='college-detail'),

    path('departments/', views.DepartmentView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', views.DepartmentView.as_view(), name='department-detail'),
]
