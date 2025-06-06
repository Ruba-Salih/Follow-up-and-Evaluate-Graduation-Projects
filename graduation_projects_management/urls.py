"""
URL configuration for graduation_projects_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.land, name="land"),
    
    path("university/", include("university.urls")),

    path("api/users/", include("users.urls")),
    path("admin-home/home/", views.admin_home, name="admin-home"),
    path("coordinator/home/", views.coordinator_home, name="coordinator-home"),
    path("student/home/", views.student_home, name="student-home"),
    path("teacher/home/", views.teacher_home, name="teacher-home"),

    #The form urls
    path('api/form/', include('form.urls')),

    # The project urls
    path('api/project/', include('project.urls')),

    path('grade/', include('grades.urls')),
    path('teacher/', include('grades.urls')),

    #The meeting urls
    path('', include('meeting.urls')),

    #notifications urls
    path('notifications/', include('notifications.urls')),

    #feedbacks urls
    path('feedbacks/', include('feedbacks.urls')),

    #reports urls
    path("api/report/", include("report.urls")),

    # Announcement app API routes
    path('api/announcements/', include('announcement.urls')),

    path('i18n/', include('django.conf.urls.i18n')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)