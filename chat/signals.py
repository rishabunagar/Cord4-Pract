from django.db.models.signals import post_save
from django.dispatch import receiver

from common.helper import create_cronjob, manage_periodic_task
from .models import Event, MessageSetting, RecurringMessage
from datetime import timedelta


@receiver(post_save, sender=Event)
def event_creation(sender, created, instance, **kwargs):
    """
    Signal receiver function triggered after saving an Event object.

    This function is called when an Event object is created. It creates a cron job
    to handle event-related tasks, such as sending event messages. It utilizes
    the `create_cronjob` function to create a cron job based on the event's schedule.
    Then, it manages the periodic task using the `manage_periodic_task` function.

    Args:
        sender: The model class that sends the signal (Event in this case).
        created (bool): A boolean indicating whether the Event instance was created.
        instance: The Event instance that was saved.
        **kwargs: Additional keyword arguments passed to the function.

    """

    if created:
        crontab_obj = create_cronjob(instance.schedule_on)
        data = {
            "title": f"event task - {instance.title}",
            "task": "chat.tasks.send_event_message",
            "task_data": {"event_id": instance.id},
        }
        manage_periodic_task(data, crontab_obj)


@receiver(post_save, sender=MessageSetting)
def message_setting_creation(sender, created, instance, **kwargs):
    """
    Signal receiver function triggered after saving a MessageSetting object.

    This function is called when a MessageSetting object is created or updated.
    It ensures that only the newly created or updated MessageSetting instance is
    marked as active, while all other instances are set to inactive. This behavior
    maintains the uniqueness of the active setting.

    Args:
        sender: The model class that sends the signal (MessageSetting in this case).
        created (bool): A boolean indicating whether the MessageSetting instance was created.
        instance: The MessageSetting instance that was saved.
        **kwargs: Additional keyword arguments passed to the function.

    """
    MessageSetting.objects.exclude(id=instance.id).update(is_active=False)


@receiver(post_save, sender=RecurringMessage)
def manage_recurring_msg(sender, created, instance, **kwargs):
    """
    Signal receiver function triggered after saving a RecurringMessage object.

    This function is called when a RecurringMessage object is created. It generates
    scheduled messages based on the recurrence pattern specified in the RecurringMessage
    instance. It calculates the schedule dates between the start and end dates, and for
    each schedule date, it creates a cron job using the `create_cronjob` function. It
    then manages the periodic task using the `manage_periodic_task` function.

    Args:
        sender: The model class that sends the signal (RecurringMessage in this case).
        created (bool): A boolean indicating whether the RecurringMessage instance was created.
        instance: The RecurringMessage instance that was saved.
        **kwargs: Additional keyword arguments passed to the function.

    """

    if created:
        start_date = instance.start_date
        end_date = instance.end_date
        schedule = instance.schedule
        schedule_dates = []
        current_date = start_date
        while current_date <= end_date:
            schedule_dates.append(current_date)
            if schedule == "daily":
                current_date += timedelta(days=1)
            elif schedule == "weekly":
                current_date += timedelta(weeks=1)
            elif schedule == "monthly":
                current_date = current_date.replace(day=1) + timedelta(days=31)

        data = {
            "title": f"Message task - {instance.message.content}",
            "task": "chat.tasks.create_schedule_message",
            "task_data": {
                "is_recurring": True,
                "content": instance.message.content,
                "sender_id": instance.message.sender.id,
            },
        }

        for schedule_date in schedule_dates:
            crontab_obj = create_cronjob(schedule_date)
            manage_periodic_task(data, crontab_obj)
