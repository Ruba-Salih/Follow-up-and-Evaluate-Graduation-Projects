from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnouncementViewSet, AnnouncementCreateView, manage_announcements, announcement_edit

router = DefaultRouter()
router.register(r'announcement', AnnouncementViewSet, basename='announcement')

urlpatterns = [
    path('', include(router.urls)),
    path('create/', AnnouncementCreateView.as_view(), name='announcement-create'),
    path('manage-expired/', manage_announcements, name='manage_announcements'),
    path('announcement/<int:announcement_id>/edit/', announcement_edit, name='announcement_edit'),
]
