from django.http import JsonResponse
from django.views.decorators.http import require_GET

from quran.selectors.ayah import search_ayahs


@require_GET
def live_search(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    ayahs = search_ayahs(query)

    results = [
        {
            "id": ayah.id,
            "surah_name": ayah.surah.name_fa,
            "surah_number": ayah.surah.number,
            "ayah_number": ayah.number,
            "text_prefix": ayah.text_prefix or ayah.text[:20],
        }
        for ayah in ayahs
    ]

    return JsonResponse(
        {"results": results},
        json_dumps_params={"ensure_ascii": False},
    )