# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FeedbackForm


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
