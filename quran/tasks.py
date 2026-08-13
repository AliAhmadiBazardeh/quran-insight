import requests
from celery import shared_task
from django.contrib.auth import get_user_model

from .models import Tafsir
from .services.bale import send_tafsir_notification, send_feedback_notification

User = get_user_model()


@shared_task(
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_tafsir_notification_task(
    *,
    obj_id: int,
    user_id: int,
    change: bool,
):
    obj = Tafsir.objects.get(pk=obj_id)
    user = User.objects.get(pk=user_id)

    return send_tafsir_notification(
        obj=obj,
        user=user,
        change=change,
    )

@shared_task(
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_feedback_notification_task(
    *,
    feedback_type: str,
    text: str,
):
    return send_feedback_notification(
        feedback_type=feedback_type,
        text=text,
    )