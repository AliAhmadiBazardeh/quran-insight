from django.db.models import QuerySet
from quran.models import TafsirSource
from quran.models import Tafsir


def get_tafsirs_for_ayah(ayah_id: int) -> QuerySet[Tafsir]:
    return (
        Tafsir.objects
        .filter(ayah_list__id=ayah_id)
        .select_related("tafsir_source")
        .order_by("tafsir_source__order_priority")
    )


def get_tafsir_sources():
    return TafsirSource.objects.order_by("order_priority")