from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", views.login_view, name="login-page"),
    path("login/", views.UserLoginAPIView.as_view(), name="login"),

    path("logout/", views.UserLogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
