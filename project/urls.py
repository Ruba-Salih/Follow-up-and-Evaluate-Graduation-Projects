from django.urls import path
from . import views

urlpatterns = [

    # Project Proposal
    path('manage-proposals/', views.manage_proposals_view, name='manage-proposals'),
    path('proposals/', views.ProjectProposalView.as_view(), name='proposal-list-create'),
    path('proposals/<int:pk>/', views.ProjectProposalView.as_view(), name='proposal-detail'),
    path('coordinator/manage-proposals/', views.coordinator_proposals_view, name='coordinator-manage-proposals'),
    path('teacher/manage-proposals/', views.teacher_proposals_view, name='teacher-manage-proposals'),
    path('teacher/student-proposals/', views.student_proposals_view, name='student-proposals'),

    # Feedback Exchange
    path('feedback/', views.FeedbackExchangeView.as_view(), name='feedback-exchange'),

    # Project
    path("projects/page/", views.manage_project_landing_view, name="manage-project-landing"),
    path('manage-projects/', views.manage_projects_view, name='manage-projects'),
    path("projects/", views.ProjectView.as_view(), name="project-list-create"),
    path("projects/<int:pk>/", views.ProjectView.as_view(), name="project-detail"),

    # Track Project
    #path("project/track/page/", views.track_projects_landing_view, name="track-project-page"),
    #path("project/track/page/<int:pk>/", views.track_project_view, name="track-project-page-pk"),

    path("project/track/", views.TrackProjectView.as_view(), name="track-project-list"),
    path("project/track/<int:pk>/", views.TrackProjectView.as_view(), name="track-project-detail"),

    path("project/my/", views.student_project_page, name="student-projects"),

    path("project/teacher/", views.teacher_projects_page, name="teacher_projects"),

    path('project/tasks/', views.project_tasks_page, name='project-tasks-page'),
    path("tasks/<int:task_id>/", views.get_task_detail, name="task-detail"),

    path("available-projects/", views.available_projects_view, name="available-projects"),
    path("projects/available/action/", views.AvailableProjectActionView.as_view(), name="available-project-action"),
    path("available/<int:project_id>/", views.AvailableProjectActionView.as_view(), name="available-project-action-item"),
    path("project/view/<int:project_id>/", views.teacher_view_project, name="project-detail"),
    path('project/<int:project_id>/progress/', views.project_progress_view, name='project_progress'),


]
