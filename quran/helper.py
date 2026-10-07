import re
import requests
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


PERSIAN_REPLACEMENTS = {
    'ك': 'ک',  # Arabic kaf -> Persian kaf
    'ي': 'ی',  # Arabic ye -> Persian ye
    'ة': 'ه',  # ta marbuta -> he (optional)
    'ى': 'ی',  # alef maksura -> ye
    'إ': 'ا',  # alef with hamza below -> alef
    'أ': 'ا',  # alef with hamza above -> alef
    'آ': 'ا',  # alef madd -> alef (or keep as آ? common to keep)
    'ٱ': 'ا',  # alef wasl
    'ا۟': 'ا',  # vaghf
}

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
    replacements = PERSIAN_REPLACEMENTS

    for old, new in replacements.items():
        text = text.replace(old, new)

    # 4. Remove leading "ال" if present
    if text.startswith("ال") and text_type == 'surah':
        text = text[2:]   # remove first two characters

    # Optional: normalize multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_persian_with_mapping(
    text_type: str,
    text: str,
) -> tuple[str, list[tuple[int, int]]]:
    """
    Normalize Arabic/Persian text while keeping a mapping
    from normalized characters back to the original text.

    Each mapping item is:

        (original_start, original_end)

    for the corresponding normalized character.
    """

    if not text:
        return text, []

    normalized_chars: list[str] = []
    mapping: list[tuple[int, int]] = []

    i = 0

    while i < len(text):
        start = i
        char = text[i]

        # Handle the special Quranic sequence: ا۟
        if text.startswith("ا۟", i):
            normalized_chars.append("ا")
            mapping.append((i, i + 2))
            i += 2
            continue

        # Normalize consecutive whitespace into one space.
        if char.isspace():
            while i < len(text) and text[i].isspace():
                i += 1

            if normalized_chars and normalized_chars[-1] != " ":
                normalized_chars.append(" ")
                mapping.append((start, i))

            continue

        # Move past the current character.
        i += 1

        # Include removable Quranic diacritics/marks
        # in the original span of this normalized character.
        while i < len(text):
            current = text[i]

            if (
                '\u064B' <= current <= '\u065F'
                or current == '\u0670'
            ):
                i += 1
                continue

            break

        normalized_char = PERSIAN_REPLACEMENTS.get(char, char)

        if normalized_char:
            normalized_chars.append(normalized_char)
            mapping.append((start, i))

    # Equivalent to .strip(), but keep mapping aligned.
    while normalized_chars and normalized_chars[0] == " ":
        normalized_chars.pop(0)
        mapping.pop(0)

    while normalized_chars and normalized_chars[-1] == " ":
        normalized_chars.pop()
        mapping.pop()

    # Existing behavior:
    # Remove leading "ال" only for surah names.
    if text_type == "surah" and "".join(normalized_chars).startswith("ال"):
        del normalized_chars[:2]
        del mapping[:2]

    return "".join(normalized_chars), mapping

TAFSIR_SOURCE_COLORS = [
    "#5470c6",
    "#91cc75",
    "#fac858",
    "#ee6666",
    "#73c0de",
    "#3ba272",
    "#fc8452",
    "#9a60b4",
]
