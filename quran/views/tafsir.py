from django.http import JsonResponse
from django.views.decorators.http import require_GET

from quran.models import Ayah
from quran.selectors.tafsir import get_tafsirs_for_ayah


@require_GET
def get_tafsir(request):
    ayah_id = request.GET.get("ayah_id")

    if not ayah_id:
        return JsonResponse(
            {"error": "ayah_id parameter is required"},
            status=400,
        )

    try:
        ayah = (
            Ayah.objects
            .select_related("surah")
            .get(id=ayah_id)
        )
    except Ayah.DoesNotExist:
        return JsonResponse(
            {"error": "Ayah not found"},
            status=404,
        )

    tafsirs = get_tafsirs_for_ayah(ayah.id)

    data = []

    for tafsir in tafsirs:
        other_ayahs = (
            tafsir.ayah_list
            .exclude(id=ayah.id)
            .values("number")
        )

        data.append(
            {
                "id": tafsir.id,
                "source": tafsir.tafsir_source.title,
                "text": tafsir.text,
                "same_tafsir_numbers": [
                    {
                        "ayah_number": item["number"],
                    }
                    for item in other_ayahs
                ],
            }
        )

    return JsonResponse(
        {
            "tafsirs": data,
            "count": len(data),
            "ayah": {
                "id": ayah.id,
                "surah_name": ayah.surah.name_fa,
                "surah_number": ayah.surah.number,
                "ayah_number": ayah.number,
                "text": ayah.text,
                "text_prefix": ayah.text_prefix,
            },
        },
        json_dumps_params={"ensure_ascii": False},
    )