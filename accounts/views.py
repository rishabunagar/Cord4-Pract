import ast
import random

from django.contrib.auth import login
from django.urls import reverse
from django.utils.encoding import smart_bytes
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import User
from .serializers import UserSerializer, LoginSerializer, OtpVerifySerializer


class UserCreateAPIView(CreateAPIView):
    """
    API view for creating new user accounts.

    This view allows users to create new accounts by submitting their details.
    It uses the UserSerializer for validating and saving user data.

    Attributes:
        queryset: A queryset representing all User objects.
        serializer_class: The serializer class used for validating and saving user data.
        permission_classes: A list of permission classes allowing unrestricted access to create user accounts.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserRetrieveView(RetrieveUpdateAPIView):
    """
    API view for retrieving and updating user accounts.

    This view allows users to retrieve and update their account details.
    It uses the UserSerializer for serializing and deserializing user data.

    Attributes:
        queryset: A queryset representing all User objects.
        lookup_field: The field used to retrieve individual user instances (default is 'pk').
        serializer_class: The serializer class used for serializing and deserializing user data.
        permission_classes: A list of permission classes allowing unrestricted access to retrieve and update user accounts.
    """

    queryset = User.objects.all()
    lookup_field = "pk"
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class OTPLoginView(APIView):
    """
    API view for handling OTP-based user authentication.

    This view generates and sends OTPs to registered users for login purposes.

    Attributes:
        serializer_class: The serializer class used for validating phone numbers during OTP generation.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """
        POST method to generate and send OTPs to registered users for login authentication.

        Parameters:
            request: The HTTP request object containing the user's phone number.

        Returns:
            Response: HTTP response indicating whether OTP generation and sending were successful.
        """
        phone_number = request.data.get("phone_number")

        # Check if the phone number exists in the database
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"detail": "Phone number not registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate OTP
        otp = str(random.randint(1000, 9999))

        # Store the OTP associated with the user in the database
        user.otp = otp
        user.save()

        token = urlsafe_base64_encode(
            smart_bytes({"user_id": user.id, "phone_number": user.phone_number})
        )
        otp_verify_link = request.build_absolute_uri(
            reverse("accounts:otp_verify_api", kwargs={"token": token})
        )

        return Response(
            {
                "detail": "OTP sent successfully",
                "otp_verify_link": otp_verify_link,
                "otp": otp,
                "message": "You can use this otp for verify",
            },
            status=status.HTTP_200_OK,
        )


class OTPVerificationView(APIView):
    """
    API view for verifying OTPs during user authentication.

    This view verifies the OTP provided by the user during the login process.

    Attributes:
        serializer_class: The serializer class used for validating OTPs during verification.
    """

    serializer_class = OtpVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request, token):
        """
        POST method to verify the OTP provided by the user during authentication.

        Parameters:
            request: The HTTP request object containing the OTP.
            token: The token used to identify the user for OTP verification.

        Returns:
            Response: HTTP response indicating whether OTP verification was successful.
        """
        otp = request.data.get("otp")

        # Check if the phone number exists in the database
        try:
            user_info = ast.literal_eval(smart_str(urlsafe_base64_decode(token)))
            user = User.objects.filter(phone_number=user_info["phone_number"]).first()
        except User.DoesNotExist:
            return Response(
                {"detail": "Phone number not registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify OTP
        if otp != user.otp:
            return Response(
                {"detail": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        # access token for that user
        access_token = AccessToken.for_user(user=user)
        # refresh token for that user
        refresh_token = RefreshToken.for_user(user=user)

        login(request, user)

        return Response(
            {"access": str(access_token), "refresh": str(refresh_token)},
            status=status.HTTP_200_OK,
        )
