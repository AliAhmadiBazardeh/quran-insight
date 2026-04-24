from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Ayah , Tafsir

def index(request):
    return render(request, "quran/index.html")

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

    tafsirs = Tafsir.objects.filter(ayah=ayah).order_by('order_priority')

    data = []
    for t in tafsirs:
        data.append({
            'id': t.id,
            'source': t.tafsir_source.title,
            'text': t.text,
            'order_priority': t.order_priority,
        })

    return JsonResponse({'tafsirs': data, 'ayah': {
        'id': ayah.id,
        'surah_name': ayah.surah.name_fa,
        'surah_number': ayah.surah.number,
        'ayah_number': ayah.number,
        'text': ayah.text,
        'text_prefix': ayah.text_prefix,
    }}, json_dumps_params={'ensure_ascii': False})