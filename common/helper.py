from django.core.files import File
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import random, string

from chat.models import MessageSetting, Message


def save_user_img(user_data, img_data):
    """
    Save a user images
    """
    if img_data:
        file_name = img_data.name
        user_data.profile_img.save(file_name, File(img_data), save=True)
        user_data.save()
    return user_data


def create_cronjob(schedule_time):
    """
    Create a crontab objects
    """
    crontab_obj, _ = CrontabSchedule.objects.get_or_create(
        minute=schedule_time.minute,
        hour=schedule_time.hour,
        day_of_month=schedule_time.day,
        month_of_year=schedule_time.month,
        day_of_week="*",
        timezone="Asia/Kolkata",
    )
    return crontab_obj


def manage_periodic_task(data, crontab_obj):
    """
    Create a periodic task
    """
    periodic_task_obj = PeriodicTask.objects.create(
        name=f"event task - {data['title']} - {''.join(random.choice(string.ascii_lowercase) for i in range(10))}",
        task=data["task"],
        crontab=crontab_obj,
        kwargs=data["task_data"],
        one_off=True,
    )
    return periodic_task_obj


def manage_receptions_message(sender_id, content):
    """
    sent to multiple messages to receptions
    """
    message_setting = MessageSetting.objects.filter(is_active=True).first()
    messages = []
    if message_setting.is_recurring_on or message_setting.is_auto_sending_on:
        for user in message_setting.receptions.all():
            messages.append(
                Message(
                    sender_id=sender_id,
                    receiver=user.id,
                    content=content,
                )
            )

        if messages:
            Message.objects.bulk_create(messages)

    return True
