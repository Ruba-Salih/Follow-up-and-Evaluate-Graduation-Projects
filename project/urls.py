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
]
