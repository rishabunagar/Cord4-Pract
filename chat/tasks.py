from celery import shared_task

from chat.models import Event, Message
from common.helper import manage_receptions_message


@shared_task(name="send_event_message")
def send_event_message(kwargs):
    """
    Celery task for sending event messages.

    This task is responsible for sending event messages to the organizer.
    It retrieves the event ID from the provided keyword arguments and fetches
    the corresponding Event object. If the event is not marked as complete, it
    manages the reception message and marks the event as complete.

    Args:
        kwargs (dict): A dictionary containing keyword arguments. It should contain
                       the key "event_id" specifying the ID of the event.

    Returns:
        bool: True if the task is successfully executed.
    """
    event_id = kwargs["event_id"]
    event = Event.objects.filter(id=int(event_id)).first()

    if not event.is_complete:
        manage_receptions_message(event.organize_by, event.description)
        event.is_complete = True
        event.save()

    return True


@shared_task(name="create_schedule_message")
def create_schedule_message(kwargs):
    """
    Celery task for creating scheduled messages.

    This task is responsible for creating scheduled messages. It retrieves the message
    data from the provided keyword arguments. If the message is marked as recurring,
    it manages the reception message. Otherwise, it creates a new Message object.

    Args:
        kwargs (dict): A dictionary containing keyword arguments. It should contain
                       the key "task_data" which holds message-related data.
                       The "task_data" dictionary should include:
                           - "is_recurring" (bool): Indicates if the message is recurring.
                           - "sender_id" (int): ID of the message sender.
                           - "receiver_id" (int): ID of the message receiver (if applicable).
                           - "content" (str): Content of the message.

    Returns:
        bool: True if the task is successfully executed.
    """
    message_data = kwargs["task_data"]
    if "is_recurring" in message_data and message_data["is_recurring"]:
        manage_receptions_message(message_data["sender_id"], message_data["content"])
    else:
        Message.objects.create(
            sender_id=message_data["sender_id"],
            receiver_id=message_data["receiver_id"],
            content=message_data["content"],
        )
    return True
