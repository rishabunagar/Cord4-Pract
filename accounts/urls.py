from django.urls import path
from accounts.views import (
    UserCreateAPIView,
    UserRetrieveView,
    OTPLoginView,
    OTPVerificationView,
)

app_name = "accounts"

urlpatterns = [
    path("create_user", UserCreateAPIView.as_view(), name="user_create_api"),
    path("manage_user/<int:pk>", UserRetrieveView.as_view(), name="user_update_api"),
    path("login/", OTPLoginView.as_view(), name="user_login_api"),
    path("otp_verify/<token>/", OTPVerificationView.as_view(), name="otp_verify_api"),
]
