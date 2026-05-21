from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Ayah, Tafsir, TafsirSource, Surah
from django.core.paginator import Paginator
from django.db.models import Sum, Count

def index(request):
    return render(request, "quran/index.html")

def about_view(request):
    return render(request, 'quran/about.html')

def support_view(request):
    return render(request, 'quran/support.html')

def contact_view(request):
    """نمایش صفحه تماس با ما"""
    return render(request, 'quran/contact.html')

@csrf_exempt
@require_http_methods(["GET"])
def live_search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})

    # جستجو در متن آیه (متن کامل عربی)
    # برای جستجوی حروف، از icontains استفاده می‌کنیم (بدون حساسیت به حروف بزرگ/کوچک)
    # همچنین می‌توانیم Q روی شماره سوره یا آیه نیز اضافه کنیم (اختیاری)
    results = Ayah.objects.filter(
        Q(text_fa__icontains=query)
    ).select_related('surah')[:10]  # حداکثر 10 نتیجه

    data = []
    for ayah in results:
        data.append({
            'id': ayah.id,
            'surah_name': ayah.surah.name_fa,        # نام سوره به فارسی
            'surah_number': ayah.surah.number,
            'ayah_number': ayah.number,
            'text_prefix': ayah.text_prefix or ayah.text[:20],
            # 'full_text': ayah.text  # در صورت نیاز
        })

    return JsonResponse({'results': data}, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
@require_http_methods(["GET"])
def get_tafsir(request):
    ayah_id = request.GET.get('ayah_id')
    if not ayah_id:
        return JsonResponse({'error': 'ayah_id parameter is required'}, status=400)

    try:
        ayah = Ayah.objects.get(id=ayah_id)
    except Ayah.DoesNotExist:
        return JsonResponse({'error': 'Ayah not found'}, status=404)

    tafsirs = Tafsir.objects.filter(
        ayah_list__id=ayah_id
    ).order_by('tafsir_source__order_priority')

    data = []
    for t in tafsirs:
        other_ayah_list = t.ayah_list.exclude(id=ayah_id).values('number')

        data.append({
            'id': t.id,
            'source': t.tafsir_source.title,
            'text': t.text,
            'same_tafsir_numbers': [
                {
                    'ayah_number': ayah['number'],
                }
                for ayah in other_ayah_list
            ]
        })

    return JsonResponse(
        {
        'tafsirs': data,
        'count': len(data) if data else 0,
        'ayah': {
        'id': ayah.id,
        'surah_name': ayah.surah.name_fa,
        'surah_number': ayah.surah.number,
        'ayah_number': ayah.number,
        'text': ayah.text,
        'text_prefix': ayah.text_prefix,
    }}, json_dumps_params={'ensure_ascii': False})





def dashboard_view(request):
    """صفحه داشبورد با چارت‌های Pie - صفحه‌بندی شده (هر 3 سوره)"""

    tafsir_sources = list(TafsirSource.objects.all().order_by('order_priority'))

    colors = [
        '#5470c6', '#91cc75', '#fac858', '#ee6666',
        '#73c0de', '#3ba272', '#fc8452', '#9a60b4'
    ]

    global_stats = Surah.objects.aggregate(
        total_surahs=Count('id'),
        total_verses=Sum('total_verses'),
        total_ayahs_with_tafsir=Count(
            'ayahs__id',
            filter=Q(ayahs__tafsir_list__isnull=False),
            distinct=True
        )
    )

    # -------- ۲. صفحه‌بندی سوره‌ها --------
    page_number = request.GET.get('page', 1)
    all_surahs = Surah.objects.prefetch_related(
        'ayahs__tafsir_list__tafsir_source'
    ).order_by('number')  # یا 'id' به دلخواه
    paginator = Paginator(all_surahs, 3)  # هر صفحه 3 سوره
    page_obj = paginator.get_page(page_number)

    # -------- ۳. ساخت آمار فقط برای سوره‌های صفحه جاری --------
    surahs_stats = []
    for surah in page_obj.object_list:
        total_verses = surah.total_verses
        ayahs = list(surah.ayahs.all())

        ayahs_with_tafsir_set = set()
        source_ayah_map = {source.id: set() for source in tafsir_sources}

        for ayah in ayahs:
            tafsirs = list(ayah.tafsir_list.all())
            if tafsirs:
                ayahs_with_tafsir_set.add(ayah.id)
                for tafsir in tafsirs:
                    source_ayah_map[tafsir.tafsir_source_id].add(ayah.id)

        ayahs_with_tafsir = len(ayahs_with_tafsir_set)
        verses_without_tafsir = total_verses - ayahs_with_tafsir

        sources_stats = []
        for idx, source in enumerate(tafsir_sources):
            ayah_count = len(source_ayah_map[source.id])
            if ayah_count > 0:
                sources_stats.append({
                    'source_id': source.id,
                    'source_title': source.title,
                    'ayah_count': ayah_count,
                    'color': colors[idx % len(colors)]
                })

        completion_percentage = (ayahs_with_tafsir / total_verses * 100) if total_verses > 0 else 0

        surahs_stats.append({
            'surah_id': surah.id,
            'surah_name': surah.name_fa,
            'surah_number': surah.number,
            'total_verses': total_verses,
            'verses_with_tafsir': ayahs_with_tafsir,
            'verses_without_tafsir': verses_without_tafsir,
            'completion_percentage': round(completion_percentage, 2),
            'sources_stats': sources_stats
        })

    context = {
        'surahs_stats': surahs_stats,          # فقط سوره‌های صفحه جاری
        'page_obj': page_obj,                  # برای کنترل‌های صفحه‌بندی
        'tafsir_sources': [
            {
                'id': s.id,
                'title': s.title,
                'color': colors[idx % len(colors)]
            }
            for idx, s in enumerate(tafsir_sources)
        ],
        'total_sources': len(tafsir_sources),
        # آمار کلی
        'total_surahs_count': global_stats['total_surahs'],
        'total_verses_global': global_stats['total_verses'],
        'total_ayahs_with_tafsir_global': global_stats['total_ayahs_with_tafsir'],
    }

    return render(request, 'quran/dashboard.html', context)