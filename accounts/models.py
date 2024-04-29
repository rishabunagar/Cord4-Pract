from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

from common.models import Base


class User(AbstractUser, Base):
    username = None
    password = None

    email = models.EmailField("email address", unique=True)
    phone_number = models.CharField(
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: " "'+999999999'.",
            )
        ],
        max_length=17,
        unique=True,
    )
    otp = models.CharField(blank=True, null=True, max_length=50)
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        unique_together = ["email", "phone_number"]

    def __str__(self):
        return self.get_full_name()


class UserProfile(Base):
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="user_prof"
    )
    profile_img = models.ImageField(upload_to="user_img/", blank=True, null=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} - Profile"
