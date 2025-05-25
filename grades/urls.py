from django.urls import path
from . import views

urlpatterns = [
    path('form/<int:project_id>/', views.grade_form, name='grade_form'),
    path('submit_grades/<int:project_id>/', views.submit_grades, name='submit_grades'),
    path('view_grades/<int:project_id>/', views.view_grades, name='view_grades'),
    path('manage_grades/', views.manage_grades_view, name='manage_grades'),
    path('grade/success/<int:project_id>/', views.grade_success, name='grade_success'),
    path('send_grades_to_all/', views.send_grades_to_all, name='send_grades_to_all'),
    path('view_my_grade/', views.view_my_grade, name='view_my_grade'),
    #path('manage-grades/', views.manage_grades_search, name='manage_grades_search'),
    path('project/<int:project_id>/view-grades/', views.view_project, name='view_project'),
    #path('search-suggestions/', views.get_search_suggestions, name='get_search_suggestions'),
    #path('home/', views.teacher_home, name='teacher_home'),
    path('manage-projects/', views.manage_projects, name='manage_projects'),
    path('project/<int:project_id>/<str:role>/', views.project_role_dashboard, name='project_role_dashboard'),
]
