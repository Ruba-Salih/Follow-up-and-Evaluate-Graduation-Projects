from django.urls import path
from . import views

urlpatterns = [
    path('review-exchanges/', views.review_exchanges, name='review-exchanges'),
    path('reply-to-feedback/', views.reply_to_feedback, name='reply_to_feedback'),
    path('teacher/review-exchanges/', views.teacher_review_exchanges, name='teacher-review-exchanges'),
    path('delete-feedback/<int:id>/', views.delete_feedback, name='delete-feedback'),
    path('feedback/edit/<int:id>/', views.edit_feedback, name='edit-feedback'),
    path('edit-reply/<int:reply_id>/', views.edit_feedback_reply, name='edit-feedback-reply'),


]
