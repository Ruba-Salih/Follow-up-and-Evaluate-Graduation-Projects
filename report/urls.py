# reports/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("supervisor/reports/<int:project_id>/", views.supervisor_reports_page, name="supervisor-reports-page"),
    path("students/<int:project_id>/", views.get_project_students),
    path("project-reports/", views.ProjectReportView.as_view(), name="report-list-create"),
    path("project-reports/<int:pk>/", views.ProjectReportView.as_view(), name="report-detail"),

    path('track-projects/', views.track_projects_view, name='track-projects'),
    path("report-view/", views.report_view, name="report-view"),

    path("manege_reports/", views.manege_reports, name="manege-reports"),
    path('projects/', views.report_projects_view, name='report-projects'),
    path('unassigned-students/', views.report_unassigned_students_view, name='report-unassigned-students'),
    path('teacher-roles/', views.report_teacher_roles_view, name='report-teacher-roles'),
    path('proposals/', views.report_proposals_view, name='report-proposals'),
    path('projects-by-coordinator/', views.report_projects_by_coord_view, name='report-projects-by-coord'),

]
