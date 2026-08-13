from django.shortcuts import render

from quran.services.dashboard import dashboard_service


def dashboard_view(request):
    page_number = request.GET.get("page", 1)

    page_obj = dashboard_service.get_surah_list_page(
        page_number=page_number,
    )

    context = dashboard_service.build_context(
        page_obj=page_obj,
    )

    return render(
        request,
        "quran/dashboard.html",
        context,
    )