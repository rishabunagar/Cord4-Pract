from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common.helper import save_user_img
from .models import User, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer handles the serialization and deserialization of User objects,
    including creation and updating of user profiles.

    Attributes:
        profile: A SerializerMethodField representing the user's profile information.
        phone_number: CharField representing the user's phone number.
        address: CharField representing the user's address.
        profile_img: ImageField representing the user's profile image.

    Methods:
        get_profile: Method to retrieve and serialize user profile information.
        create: Method to create a new user instance and associated user profile.
        update: Method to update an existing user instance and associated user profile.
    """

    profile = serializers.SerializerMethodField()

    phone_number = serializers.CharField(
        help_text="Enter your phone-no here", required=True
    )
    address = serializers.CharField(
        write_only=True, help_text="Enter your address here", required=False
    )

    profile_img = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "profile",
            "phone_number",
            "address",
            "profile_img",
        )
        extra_kwargs = {
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
        }

    def get_profile(self, data):
        return ProfileSerializer(UserProfile.objects.filter(user=data).first()).data

    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get("email"),
            phone_number=validated_data.get("phone_number"),
        )
        profile_obj = UserProfile.objects.create(
            user_id=user.id, address=validated_data.get("address")
        )

        save_user_img(profile_obj, validated_data.get("profile_img"))
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        save_user_img(instance, validated_data.get("profile_img"))
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.

    This serializer handles the serialization and deserialization of UserProfile objects,
    specifically focusing on the user's address and profile image.

    Attributes:
        address: CharField representing the user's address.
        profile_img: ImageField representing the user's profile image.
    """

    class Meta:
        model = UserProfile
        fields = ["address", "profile_img"]


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login authentication.

    This serializer handles the validation of user phone numbers during login attempts.

    Attributes:
        phone_number: CharField representing the user's phone number (write-only).

    Methods:
        validate: Method to validate the provided phone number and check its existence in the database.
    """

    phone_number = serializers.CharField(write_only=True)

    def validate(self, data):
        if not data["phone_number"]:
            raise ValidationError({"phone_number": "Please Enter a phone no."})

        if not User.objects.filter(phone_number=data["phone_number"]).exists():
            raise ValidationError({"phone_number": "Phone-number does not exits."})

        return data


class OtpVerifySerializer(serializers.Serializer):
    """
    Serializer for OTP (One-Time Password) verification.

    This serializer handles the validation of OTPs during the authentication process.

    Attributes:
        otp: CharField representing the one-time password (write-only).

    Methods:
        validate: Method to validate the provided OTP.
    """

    otp = serializers.CharField(write_only=True)

    def validate(self, data):
        if "otp" not in data and not data["otp"]:
            raise ValidationError({"phone_number": "Please Enter an OTP."})
        return data
