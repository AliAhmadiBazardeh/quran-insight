import re

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
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # 4. Remove leading "ال" if present
    if text.startswith("ال") and text_type == 'surah':
        text = text[2:]   # remove first two characters

    # Optional: normalize multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text