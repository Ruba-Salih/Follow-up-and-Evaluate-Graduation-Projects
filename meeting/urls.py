from django.urls import path
from . import views

urlpatterns = [
    # API Endpoints
    path('api/set-available-time/', views.SetAvailableTimeAPIView.as_view(), name='set-available-time-api'),
    path('api/teachers/', views.TeacherListAPIView.as_view(), name='teacher-list-api'),
    path('api/teachers/<int:teacher_id>/available-times/', views.TeacherAvailableTimeAPIView.as_view(), name='teacher-available-times-api'),
    path('api/schedule-meeting/', views.ScheduleMeetingAPIView.as_view(), name='schedule-meeting'),
    path('schedule-meeting/', views.ScheduleMeetingView.as_view(), name='schedule-meeting-page'),
    path('api/teacher-meetings/', views.TeacherMeetingRequestsAPIView.as_view(), name='teacher-meetings'),
    path('api/upcoming-meetings/', views.UpcomingMeetingsView.as_view(), name='upcoming-meetings'),

    # Pages
    path('set-available-time/', views.set_available_time_page, name='set-available-time-page'),
    path('meetings/requests/', views.meeting_requests_page, name='meeting-requests-page'),
    path('meetings/history/', views.meeting_history_page, name='meeting-history-page'),
    path('accept-meeting/<int:meeting_id>/', views.accept_meeting, name='accept-meeting'),
    path('decline-meeting/<int:meeting_id>/', views.decline_meeting, name='decline-meeting'),
    path('update-meeting-status/<int:meeting_id>/', views.update_meeting_status, name='update-meeting-status'),
]
