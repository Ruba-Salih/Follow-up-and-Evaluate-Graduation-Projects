from django.urls import path
from users.views import UserLoginAPIView, UserLogoutAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", UserLoginAPIView.as_view(), name="login"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
