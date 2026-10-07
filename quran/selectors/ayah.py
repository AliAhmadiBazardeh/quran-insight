from django.db.models import QuerySet
from django.contrib.postgres.search import TrigramWordSimilarity

from quran.models import Ayah

def search_ayahs(query: str, limit: int = 10) -> QuerySet[Ayah]:
    return (
        Ayah.objects
        .annotate(
            similarity=TrigramWordSimilarity(
                query,
                "text_fa",
            )
        )
        .filter(similarity__gte=0.4)
        .select_related("surah")
        .order_by("-similarity")[:limit]
    )