from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login-page/", views.login_view, name="login-page"),
    path("login/", views.UserLoginAPIView.as_view(), name="login"),

    path("logout/", views.UserLogoutAPIView.as_view(), name="logout"),

    path("home/", views.home_redirect_view, name="home"),
    path("coordinator/home/", views.coordinator_home, name="coordinator-home"),
    path("student/home/", views.student_home, name="student-home"),
    path("teacher/home/", views.teacher_home, name="teacher-home"),

    path("coordinator/dashboard/", views.coordinator_dashboard, name="coordinator-dashboard"),

    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
