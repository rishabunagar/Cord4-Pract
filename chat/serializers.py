from rest_framework import serializers

from .models import Message, Event, MessageSetting, RecurringMessage


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.

    This serializer handles the serialization of Message objects, including sender and receiver names.

    Attributes:
        sender_name: CharField representing the first name of the message sender (read-only).
        receiver_name: CharField representing the first name of the message receiver (read-only).
    """

    sender_name = serializers.CharField(source="sender.first_name", read_only=True)
    receiver_name = serializers.CharField(source="receiver.first_name", read_only=True)

    class Meta:
        model = Message
        fields = [
            "sender",
            "sender_name",
            "receiver",
            "receiver_name",
            "content",
            "scheduled_time",
            "created_at",
        ]


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for the Event model.

    This serializer handles the serialization of Events objects, including title and organize name,description and schedule time.

    """

    class Meta:
        model = Event
        fields = ["title", "organize_by", "description", "schedule_on"]


class MessageSettingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message Setting model.

    This serializer handles the serialization of Message Setting objects.

    """

    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = MessageSetting
        fields = ["is_auto_sending_on", "is_recurring_on", "is_active", "receptions"]


class RecurringMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Recurring message model.

    This serializer handles the serialization of Recurring message objects.

    """

    class Meta:
        model = RecurringMessage
        fields = ["start_date", "end_date", "schedule", "message"]
