from django.db.models import Q
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.helper import create_cronjob, manage_periodic_task
from .models import Message, Event, MessageSetting,RecurringMessage
from .serializers import (
    MessageSerializer,
    EventSerializer,
    MessageSettingSerializer,
    RecurringMessageSerializer,
)


class MessageListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and create message.
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        scheduled_time = self.request.data.get("scheduled_time", None)
        if scheduled_time:
            scheduled_time = timezone.datetime.strptime(
                scheduled_time, "%Y-%m-%dT%H:%M"
            )
            crontab_obj = create_cronjob(scheduled_time)
            data = {
                "title": f"Message task - {self.request.data.get('content', None)}",
                "task": "chat.tasks" ".create_schedule_message",
                "task_data": {
                    "sender_id": self.request.data.get("sender", None),
                    "receiver_id": self.request.data.get("receiver", None),
                    "content": self.request.data.get("content", None),
                },
            }
            manage_periodic_task(data, crontab_obj)
        else:
            serializer.save()

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = Message.objects.filter(
            (Q(sender_id=user_id) | Q(receiver_id=user_id))
            & (Q(sender_id=user_id) | Q(receiver_id=user_id))
        ).select_related("sender", "receiver")
        return queryset


class ForwardMessageView(generics.CreateAPIView):
    """
    API view for forward to a message.
    """

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()

    def perform_create(self, serializer):
        message_data = Message.objects.filter(
            id=self.request.data["message_id"]
        ).first()
        serializer.save(
            sender=self.request.user,
            receiver_id=self.request.data.get("receiver"),
            content=message_data.content,
        )


class ReplyMessageView(generics.CreateAPIView):
    """
    API view for replying to a message.
    """

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()

    def perform_create(self, serializer):
        message_data = Message.objects.filter(
            id=self.request.data["message_id"]
        ).first()
        serializer.save(
            sender=self.request.user,
            receiver_id=self.request.data.get("receiver_id"),
            content=message_data.content,
            parent_id=self.request.data["message_id"],
        )


class MessageSettingListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating message settings.
    """

    serializer_class = MessageSettingSerializer
    permission_classes = [IsAuthenticated]
    queryset = MessageSetting.objects.all()

    def perform_create(self, serializer):
        serializer.save(is_acitve=True)


class EventListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating events.
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]


class RecurringMessageListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating recurring messages.
    """

    queryset = RecurringMessage.objects.all()
    serializer_class = RecurringMessageSerializer
    permission_classes = [IsAuthenticated]
