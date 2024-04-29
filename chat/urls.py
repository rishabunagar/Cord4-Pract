from django.urls import path

from chat.views import (
    MessageListCreateView,
    EventListCreateView,
    MessageSettingListCreateView,
    RecurringMessageListCreateView,
    ReplyMessageView,
    ForwardMessageView,
)

app_name = "chat"

urlpatterns = [
    path("messages/", MessageListCreateView.as_view(), name="message-list-create"),
    path("forward_message/", ForwardMessageView.as_view(), name="forward-message"),
    path("reply_message/", ReplyMessageView.as_view(), name="reply-message"),
    path("events/", EventListCreateView.as_view(), name="event-list-create"),
    path(
        "message_setting/",
        MessageSettingListCreateView.as_view(),
        name="message-settings-list-create",
    ),
    path(
        "recurring_messages/",
        RecurringMessageListCreateView.as_view(),
        name="recurring-message-list-create",
    ),
]
