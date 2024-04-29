from django.db import models
from accounts.models import User
from common.models import Base


class Message(Base):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField(blank=True, null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)

    def __str__(self):
        return self.content


class Event(Base):
    title = models.CharField(max_length=100, blank=True, null=True)
    organize_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="event_organize"
    )
    schedule_on = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class MessageSetting(Base):
    is_auto_sending_on = models.BooleanField(default=False)
    is_recurring_on = models.BooleanField(default=False)
    receptions = models.ManyToManyField(User, related_name="message_receptions")
    is_active = models.BooleanField(default=False)


class RecurringMessage(Base):
    SCHEDULE_CHOICES = (
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    )

    message = models.ForeignKey(
        "Message", on_delete=models.CASCADE, null=True, blank=True
    )
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    schedule = models.CharField(
        max_length=50, choices=SCHEDULE_CHOICES, default="daily"
    )
