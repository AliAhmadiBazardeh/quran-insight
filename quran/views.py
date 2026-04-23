from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Ayah

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
        Q(text__icontains=query)
    ).select_related('surah')[:10]  # حداکثر 10 نتیجه

    data = []
    for ayah in results:
        data.append({
            'id': ayah.id,
            'surah_name': ayah.surah.name_fa,        # نام سوره به فارسی
            'surah_number': ayah.surah.number,
            'ayah_number': ayah.number_in_surah,
            'text_prefix': ayah.text_prefix or ayah.text[:20],   # ۲۰ کاراکتر اول
            # 'full_text': ayah.text  # در صورت نیاز
        })

    return JsonResponse({'results': data})
