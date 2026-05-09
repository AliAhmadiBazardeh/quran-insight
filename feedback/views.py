from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FeedbackForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Feedback

def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'بازخورد شما با موفقیت ثبت شد. متشکریم!')
            return redirect('feedback')
    else:
        form = FeedbackForm()

    return render(request, 'feedback/feedback.html', {'form': form})


@require_POST
def report_search_problem(request):
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        if not query:
            return JsonResponse({'error': 'عبارت جستجو خالی است'}, status=400)

        Feedback.objects.create(
            feedback_type='search_problem',
            message=f'مشکل در جستجوی: {query}'
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)