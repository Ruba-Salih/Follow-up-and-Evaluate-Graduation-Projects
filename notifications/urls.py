from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification-list'),
    path('read/<uuid:notification_id>/', views.mark_notification_as_read, name='mark-notification-read'),
]
