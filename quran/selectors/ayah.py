from django.db.models import QuerySet

from quran.models import Ayah


def search_ayahs(query: str, limit: int = 10) -> QuerySet[Ayah]:
    return (
        Ayah.objects
        .filter(text_fa__icontains=query)
        .select_related("surah")
        [:limit]
    )