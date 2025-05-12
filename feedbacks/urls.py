from django.urls import path
from . import views

urlpatterns = [
    path('review-exchanges/', views.review_exchanges, name='review-exchanges'),
    path('reply-to-feedback/', views.reply_to_feedback, name='reply_to_feedback'),
    path('teacher/review-exchanges/', views.teacher_review_exchanges, name='teacher-review-exchanges'),
    path('coord/review-exchanges/', views.coord_review_exchanges, name='coord-review-exchanges'),
    path('delete-feedback/<int:id>/', views.delete_feedback, name='delete-feedback'),
    path('feedback/edit/<int:id>/', views.edit_feedback, name='edit-feedback'),
    path('edit-reply/<int:reply_id>/', views.edit_feedback_reply, name='edit-feedback-reply'),
    path('get-teacher-projects/<int:teacher_id>/', views.get_teacher_projects, name='get_teacher_projects'),
    path('project-feedbacks/', views.get_project_feedbacks, name='get_project_feedbacks'),
    path('submit/', views.submit_feedback_json, name='submit_feedback_json'),


]
