from django.db.models import QuerySet
from quran.models import Surah, Ayah
from django.db.models import Count, Q

def get_surahs_for_dashboard() -> QuerySet[Surah]:
    return (
        Surah.objects
        .prefetch_related(
            "ayahs__tafsir_list__tafsir_source",
        )
        .order_by("number")
    )

def get_dashboard_global_stats() -> dict:
    total_verses = Ayah.objects.count()
    total_surahs = Surah.objects.count()

    tafsir_stats = Surah.objects.aggregate(
        total_ayahs_with_tafsir=Count(
            "ayahs__id",
            filter=Q(ayahs__tafsir_list__isnull=False),
            distinct=True,
        )
    )

    return {
        "total_verses": total_verses,
        "total_surahs": total_surahs,
        "total_ayahs_with_tafsir": (
            tafsir_stats["total_ayahs_with_tafsir"]
        ),
    }

