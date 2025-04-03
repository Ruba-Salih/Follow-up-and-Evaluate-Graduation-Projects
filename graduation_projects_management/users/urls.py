from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login-page/", views.login_view, name="login-page"),
    path("login/", views.UserLoginAPIView.as_view(), name="login"),

    path("logout/", views.UserLogoutAPIView.as_view(), name="logout"),

    # home pages
    path("home/", views.home_redirect_view, name="home"),
    path("admin-home/home/", views.admin_home, name="admin-home"),
    path("coordinator/home/", views.coordinator_home, name="coordinator-home"),
    path("student/home/", views.student_home, name="student-home"),
    path("teacher/home/", views.teacher_home, name="teacher-home"),

    # dashbord pages
    path("coordinator/dashboard/", views.coordinator_dashboard, name="coordinator-dashboard"),

    # home pages
    # for admin
    path("manage-coordinators/", views.SuperCoordinatorView.as_view(), name='manage-coordinators'),
    path("manage-coordinators/<int:pk>/", views.SuperCoordinatorView.as_view()),

    # for coord
    path("manage-accounts/", views.ManageAccountsView.as_view(), name="manage-accounts"),
    path("manage-accounts/<int:user_id>/", views.ManageAccountsView.as_view(), name="edit-user"),
    path("manage-accounts/delete/<int:user_id>/", views.ManageAccountsView.as_view(), name="delete-user"),

    # profile pages
    path("profile/", views.profile_page, name="profile-page"),
    path('profile/api/', views.ProfileView.as_view(), name='profile'),
    path('profile/change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
