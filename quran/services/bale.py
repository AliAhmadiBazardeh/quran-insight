import requests

from django.conf import settings


def send_message_to_channel(*, message: str, chat_id: str):
    parameters = {
        "chat_id": chat_id,
        "text": message,
    }

    response = requests.post(
        settings.URL,
        data=parameters,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def send_tafsir_notification(*, obj, user, change):
    action = "📝 ویرایش" if change else "☑️ ایجاد"
    username = user.full_name or user.username

    message = (
        f"📖 {obj}\n"
        f"👤 توسط *🌟{username}*🌟\n"
        f"{action} شد."
    )

    return send_message_to_channel(
        chat_id=settings.BALE_CHAT_ID,
        message=message,
    )


def send_feedback_notification(*, feedback_type, text):
    message = (
        f"*{feedback_type}*\n\n"
        f"{text}"
    )

    return send_message_to_channel(
        chat_id=settings.BALE_FEEDBACK_CHANNEL_ID,
        message=message,
    )