import re
import requests
import json
from django.conf import settings

def send_message_to_channel(request,obj, change):

    action = "📝 ویرایش"
    info = str(obj)
    if not change:
        action = "☑️ ایجاد"

    message = (
        f"📖 {info}\n "
        f"👤 توسط *🌟{request.user.full_name or request.user.username}*🌟\n "
        f"{action} شد."
    )

    parameters = {
        "chat_id": settings.BALE_CHAT_ID,
        "text": message
    }

    response = requests.post(settings.URL, data=parameters)

    if response.status_code == 200:
        print(response.json())
    else:
        print("error", response.status_code)

def send_feedback_to_channel(feedback_type, text):
    message = (
        f"*{feedback_type}*\n\n "
        f"{text} "
    )

    parameters = {
        "chat_id": settings.BALE_FEEDBACK_CHANNEL_ID,
        "text": message
    }

    response = requests.post(settings.URL, data=parameters)

    if response.status_code == 200:
        print(response.json())
    else:
        print("error", response.status_code)

def normalize_persian(text_type: str, text: str) -> str:
    """Remove diacritics & normalize Persian/Arabic letters."""
    if not text:
        return text

    # 1. Remove harakat (diacritics): َ ِ ُ ً ٍ ٌ ْ etc.
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)

    # 2. Remove extra tashdid (shadda) if any, though it's already covered above
    #    but be explicit:  ّ  (U+0651)
    text = re.sub(r'\u0651', '', text)

    # 3. Normalize common problematic letters
    replacements = {
        'ك': 'ک',   # Arabic kaf -> Persian kaf
        'ي': 'ی',   # Arabic ye -> Persian ye
        'ة': 'ه',   # ta marbuta -> he (optional)
        'ى': 'ی',   # alef maksura -> ye
        'إ': 'ا',   # alef with hamza below -> alef
        'أ': 'ا',   # alef with hamza above -> alef
        'آ': 'ا',   # alef madd -> alef (or keep as آ? common to keep)
        'ٱ': 'ا',    # alef wasl
        'ا۟': 'ا',    # vaghf
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # 4. Remove leading "ال" if present
    if text.startswith("ال") and text_type == 'surah':
        text = text[2:]   # remove first two characters

    # Optional: normalize multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text