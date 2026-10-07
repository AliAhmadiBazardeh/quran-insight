from django.http import JsonResponse
from django.views.decorators.http import require_GET

from quran.selectors.ayah import search_ayahs
from quran.utilities.match_ayah import find_match_context


@require_GET
def live_search(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    ayahs = search_ayahs(query)

    results = []

    for ayah in ayahs:
        match = find_match_context(
            query=query,
            original_text=ayah.text,
        )

        results.append(
            {
                "id": ayah.id,
                "surah_name": ayah.surah.name_fa,
                "surah_number": ayah.surah.number,
                "ayah_number": ayah.number,

                "text": match["text"],
                "match_start": match["highlight_start"],
                "match_end": match["highlight_end"],
            }
        )

    return JsonResponse(
        {"results": results},
        json_dumps_params={"ensure_ascii": False},
    )